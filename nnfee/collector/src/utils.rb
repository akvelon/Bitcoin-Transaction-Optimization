def block block_index
  block_hash = $btc.getblockhash block_index
  $btc.getblock block_hash
end

def block_stats b
  transaction_keys = %w(txid hash time first_seen double_spend size vsize input_amount_int output_amount_int fee_int coinbase)
  block_keys = %w(height hash size stripped_size time first_seen difficulty input_count output_count input_amount_int output_amount_int fees_int transaction_count transactions)

  b['transactions'] = b['transactions']
    .collect { |tx| tx.delete_if { |k,v| !transaction_keys.include?(k) } }
    .select { |tx| tx['double_spend'] == false && tx['coinbase'] == false }

  b.delete_if { |k,v| !block_keys.include?(k) }
end

# To verify data integrity, its a good idea to easily check headers and how
# many unique elements there are on the last column of the CSV
def preview_output path
  puts `head #{path}`

  last_columns = []
  open(path) do |csv|
    csv.each_line do |line|
      last_columns.push(line.split(',').last.strip)
    end
  end
  p Hash[last_columns.sort.group_by {|x| x}.map {|k,v| [k,v.count]}]
end

def prepare_nn_files(input_path)
  output_training = 'fee_training.csv'
  output_test = 'fee_test.csv'
  divider = 10 # 1 in 10 will be added to the test data

  unless File.exists? input_path
    puts "File #{input_path} does not exist"
    exit 1
  end

  first_line = open(input_path).gets

  open(input_path) do |csv|
    open(output_training, 'w') do |training|
      training.puts first_line

      open(output_test, 'w') do |test|
        test.puts first_line

        index = 0
        csv.each_line do |line|
          next if line == first_line
          index += 1
          (index % divider == 0 ? test : training).puts line
        end
      end
    end
  end

  puts "\n#{output_training}"
  preview_output output_training

  puts "\n#{output_test}"
  preview_output output_test
end

def get_latest_block_id_before(db, start_block_id, time)
  currentId = start_block_id
  max_attempts = 10
  attempt = 1
  loop do
    block = block_stats (db.read start_block_id)
    if block['first_seen'] < time
      return currentId
    end
    attempt += 1
    if attempt > max_attempts
      puts "we reached the max of block to read"
      return currentId
    end
    currentId -= 1
  end
end

def median array
  sorted = array.sort
  len = sorted.length
  (sorted[(len - 1) / 2] + sorted[len / 2]) / 2.0
end

def raw_read_with_mempool db, mempool, block_id
  flattening = Time.now
  full_block = db.read block_id
  block = block_stats full_block

  subset = mempool.subset_for block['transactions']

  transactions = []
  raw_transactions = block['transactions']
  if raw_transactions.length > 0
    tx_fees_per_byte = raw_transactions.map { |tx| tx['fee_int'].to_f / tx['size'].to_f }
    tx_fees_per_byte
    block_min_fee_per_byte = tx_fees_per_byte.min
    block_median_fee_per_byte = median tx_fees_per_byte
  end
  raw_transactions.each do |tx|
    tx_first_seen = tx['first_seen']
    closest = mempool.closest_mempool(subset, tx_first_seen)

    if closest.nil?
      puts "Could not find mempool for #{tx_first_seen} (#{tx['txid']})"
      next
    end

    keys = mempool.closest_mempool_keys(subset, tx_first_seen).take(3).sort # want to calculate non-negative derivative
    if (keys.length < 3)
      puts 'Not enough keys to calc derivative'
      next
    end
    mapped_data = keys.map { |k| {'key' => k.to_i, 'value' => mempool.mempool_for(k)['pending_fee'].to_f}}
    if (mapped_data[0]['value'] > mapped_data[1]['value'])
      kvp1, kvp2 = mapped_data.drop(1)
    else
      kvp1, kvp2 = mapped_data.take(2)
    end

    dy = kvp2['value'] - kvp1['value']
    dx = kvp2['key'] - kvp1['key']
    fee_change_speed = dy.to_f / dx.to_f
    if fee_change_speed < 0
      puts "We hit in really uncommon situation when multiple blocks one by one mined, dropping from output"
      next
    end
    # latest_block_id_before = get_latest_block_id_before(db, block_id.to_i - 1, tx_first_seen)
    # blocks_to_process = block_id.to_i - latest_block_id_before
    fee_per_byte = tx['fee_int'].to_f / tx['size'].to_f
    mempool_tx_count = closest['count']
    mempool_bytes = closest['size'].to_i
    mempool_megabytes = mempool_bytes / 1024.to_f / 1024.to_f
    seconds_to_confirm = (Time.at(block['first_seen']) - Time.at(tx_first_seen)).to_i

    transactions.push({
      'txid' => tx['txid'],
      'size' => tx['size'],
      'vsize' => tx['vsize'],
      'fee' => tx['fee_int'],
      'first_seen' => tx_first_seen,

      # 'blocks_to_process' => blocks_to_process,
      'block_min_fee_per_byte' => block_min_fee_per_byte,
      'block_median_fee_per_byte' => block_median_fee_per_byte,
      'fee_change_speed' => fee_change_speed,
      'fee_per_byte' => fee_per_byte.to_f.round(2),
      'mempool_bytes' => mempool_bytes,
      'mempool_megabytes' => mempool_megabytes.to_f.round(8),
      'mempool_tx_count' => mempool_tx_count,
      'seconds_to_confirm' => seconds_to_confirm
    })
  end
  db.log "Flatten #{block_id} took #{(Time.now - flattening).round(2)} seconds"

  {
    'height' => block_id,
    'time' => block['time'],
    'first_seen' => block['first_seen'],
    'transactions' => transactions
  }
end

def write_tx f, tx, keys
  values = Array.new(keys.length)
  # sub_hash = tx.select { |k,v| keys.include?(k.to_sym) }
  tx.each { |k,v| if keys.include?(k.to_sym) then values[keys.index k.to_sym] = v end }
  # line = sub_hash.values.join(',')
  line = values.join(',')
  # throw 'missing data' if sub_hash.values.size != keys.size
  f.write "#{line}\n"
end

def add_date_time tx
  tx['date_time'] = Time.at(tx['first_seen']).to_datetime
end

def add_block_id(tx, block_id)
  tx['block_id'] = block_id
end

def add_confirmation_speed tx
  if tx['seconds_to_confirm'] <= 60 * 15    # 15 minutes
    amount = 0
  elsif tx['seconds_to_confirm'] <= 60 * 30 # 30 minutes
    amount = 1
  elsif tx['seconds_to_confirm'] <= 60 * 60 * 1  # 1 hour
    amount = 2
  elsif tx['seconds_to_confirm'] <= 60 * 60 * 4  # 4 hours
    amount = 3
  elsif tx['seconds_to_confirm'] <= 60 * 60 * 12 # 12 hours
    amount = 4
  elsif tx['seconds_to_confirm'] <= 60 * 60 * 24 * 1 # 1 day
    amount = 5
  elsif tx['seconds_to_confirm'] <= 60 * 60 * 24 * 3 # 3 days
    amount = 6
  else
    amount = 7
  end
  tx['confirmation_speed'] = amount
end

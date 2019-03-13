#!/usr/bin/env ruby

# Reads blocks stored locally and creates an output file for trainig
# min: 2017-03-01
# max: 2018-03-01

require './src/all'

output_dir = '/data/out'
FileUtils.mkdir_p output_dir

keys = %i(fee_per_byte mempool_bytes confirmation_speed fee_change_speed block_median_fee_per_byte block_id)
periods = ['2018-12']
# periods = ['2018-12', '2019-01']
# periods = ['2017-10', '2017-09', '2017-08', '2017-07']
# periods = ['2017-06', '2017-05', '2017-04', '2017-03']

data_path = '/data/data'
all_blocks = Dir["#{data_path}/*gz"].collect { |e| e.split('/').last.split('.').first.to_i }.sort
all_blocks.each do |block_id|
  $slim_db.read(block_id)
end

periods.each do |period|
  puts "Preparing #{period}"
  time = Time.now

  target_year, target_month = period.split('-').map { |e| e.to_i }

  from = Date.civil(target_year, target_month, 1).to_s
  to = Date.civil(target_year, target_month, -1).to_s

  path_id = period.gsub('-','')
  training_path = File.join(output_dir, "#{path_id}_training.csv")
  # test_path = File.join(output_dir, "#{path_id}_test.csv")
  all_blocks = $slim_db.all_local_blocks(from, to)

  i = 0
  # open(test_path, 'w') do |test_f|
    open(training_path, 'w') do |training_f|
      training_f.write "#{keys.join(',')}\n"
      # test_f.write "#{keys.join(',')}\n"

      while !all_blocks.empty?
        newest_block_id = all_blocks.pop
        $slim_db.read(newest_block_id)['transactions'].each do |tx|
          add_confirmation_speed(tx)
          add_block_id(tx, newest_block_id)
          #add_date_time(tx)
          write_tx(training_f, tx, keys)
          i += 1
        end
      end
    # end
  end

  preview_output(training_path)
  # preview_output(test_path)
  puts "Total time preparing #{period}: #{(Time.now - time).round(2)} seconds"
end

# output_file = ENV['PREPARE_OUTPUT_FILE'] || 'out.csv'
# prepare_nn_files(output_file)

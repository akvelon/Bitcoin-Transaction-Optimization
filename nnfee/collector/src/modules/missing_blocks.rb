module MissingBlocks
  def fetch_missing greater_than
    find_missing_blocks.each do |missing|
      if missing > greater_than
        begin
          read missing
        rescue
          puts "miss: Error reading #{missing}"
        end
      end
    end
  end

  def find_missing_blocks
    blockz = all_local_blocks
    if blockz.empty?
      log 'You have no blocks'
    else
      missing_blocks = (blockz.first..blockz.last).to_a - blockz
      if missing_blocks.empty?
        log 'No missing blocks'
      else
        log 'Missing blocks:'
        p missing_blocks
      end
    end
  end
end

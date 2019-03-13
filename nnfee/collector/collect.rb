#!/usr/bin/env ruby

# Collects blocks/txes/mempool data and stores it locally for analysis

require './src/all'

loop do
  last_block_index = API.next_block
  puts "api : Last block index: #{last_block_index}"
  $slim_db.read last_block_index
  if last_block_index <= 2
    puts 'all blocks downloaded'
    break
  end
end

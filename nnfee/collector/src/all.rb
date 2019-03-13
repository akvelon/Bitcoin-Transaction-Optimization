require 'date'
require 'fileutils'
require 'json'
require 'net/http'

require './src/modules/missing_blocks'
require './src/modules/validation'
require './src/modules/navigation'

require './src/api'
require './src/btc'
require './src/utils'
require './src/db'
require './src/index'
require './src/mempool'

puts 'Staring collector'

def debugger_help
  puts "\n" * 2

  puts <<-EOS
  Welcome to the collector debugger.

  $db, $mempool, $slim_db

  $slim_db.validate_index
  $slim_db.fetch_missing 467000
  $slim_db.random_tx

  EOS
end

$db = DB.new
$mempool = Mempool.new
$slim_db = SlimDB.new(nil, 'slim')
$slim_db.set($db, $mempool)

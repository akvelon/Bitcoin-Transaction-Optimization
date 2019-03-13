require 'zlib'

# Responsbile for storing the blockchain on disk
# Blocks are compressed using zlib and decompressed on the fly
class DB
  attr_accessor :db_path, :data_path, :time_index, :obj_type

  include MissingBlocks
  include Validation
  include Navigation

  def initialize(db_path = nil, obj_type = 'data')
    @db_path = ENV['DB_PATH'] || data_path || 'db'
    @obj_type = obj_type
    @data_path = File.join(@db_path, @obj_type)
    @time_index = Index.new(@db_path, "#{obj_type}_time".to_sym)
    do_validation
  end

  def read block_index
    time = Time.now
    if _have? block_index
      file_path = block_path(block_index)
      data = _read_gzip(file_path)
    else
      data = read_from_api(block_index)
      _write(block_index, data)
    end
    @time_index.add block_index, data['time']

    log "Reading #{block_index} (#{Time.at(data['time'])}) took #{(Time.now - time).to_f.round(2)} seconds"
    data
  end

  def random_tx
    read(all_local_blocks.shuffle.first)['transactions'].shuffle.first
  end

  def read_from_api block_index
    API.block_api block_index
  end

  def log s
    puts "#{obj_type}: #{s}"
  end

  private

  def _write block_index, data
    file_path = File.join(data_path, "#{block_index}.gz")
    file_path = block_path(block_index)
    Zlib::GzipWriter.open(file_path) do |gzip|
      gzip << data.to_json
      gzip.close
    end
    log "Wrote block #{block_index} with time #{Time.at(data['time'])}"
  end

  def _read_gzip file_path
    JSON.parse(Zlib::GzipReader.open(file_path) { |gzip| gzip.read })
  end
end

class SlimDB < DB
  attr_accessor :db, :mempool

  def set db, mempool
    @db = db
    @mempool = mempool
  end

  def validate
    validate_index if ENV['NO_VALIDATION'].nil?
  end

  def read_from_api block_index
    raw_read_with_mempool @db, @mempool, block_index
  end
end

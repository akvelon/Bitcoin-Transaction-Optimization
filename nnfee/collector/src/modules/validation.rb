module Validation
  def mkdirs
    FileUtils.mkdir_p data_path
  end

  def view_stats
    gzs = Dir["#{data_path}/*.gz"]
    cmd_output = `du -h #{db_path}`
    log "\n#{cmd_output}"
    log " count: #{gzs.size}"
  end

  def do_validation
    log 'Validating'
    mkdirs
    view_stats
    validate
    log 'Done validating'
  end

  def validate
  end

  def validate_index
    index_time = Time.now
    log 'Adding missing indexes'
    i = 0
    (all_local_blocks - @time_index.indexed_keys).each do |missing|
      i += 1
      read missing
      if i % 1000 == 0
        @time_index.commit
      end
    end
    @time_index.commit
    log "Done adding missing indexes #{(Time.now - index_time).round(0)} seconds"
  end
end

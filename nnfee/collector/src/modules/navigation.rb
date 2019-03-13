module Navigation
  def all_local_blocks from=nil, to=nil
    result = []
    all_blocks = Dir["#{data_path}/*gz"].collect { |e| e.split('/').last.split('.').first.to_i }.sort
    if from.nil? && to.nil?
      # return raw block indexes from disk
      result = all_blocks
    else
      # using the time index, only return blocks between the two dates
      throw 'from or to date nil' if from.nil? || to.nil?
      from_date = Date.parse(from)
      to_date = Date.parse(to)
      to_return = []
      all_blocks.each do |block_id|
        if Time.at(@time_index.data[block_id.to_s].to_i).to_date.between?(from_date, to_date)
          to_return.push block_id.to_i
        end
      end
      result = to_return.sort
    end
    log "Estimated time to read #{result.size} blocks: #{(result.size * 0.2 / 60).round(0)} minutes"
    result
  end

  def block_path block_index
    File.join(@data_path, "#{block_index}.gz")
  end

  def oldest_block_index
    Dir["#{data_path}/*.gz"].sort.first.split('/').last.split('.').first.to_i
  rescue
    nil
  end

  private

  def _have? block_index
    file_path = block_path(block_index)
    File.exists?(file_path) && !File.zero?(file_path)
  end
end

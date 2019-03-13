class Index
  attr_accessor :target, :data

  def initialize(db_path, target)
    @target = target
    @path = File.join(db_path, "#{target}.index")
    @data = {}
    @separator = ','
    @added = false

    if File.exists? @path
      open(@path) do |f|
        f.each_line do |line|
          kv = line.strip.split(@separator)
          @data[kv[0].to_s] = kv[1]
        end
      end
    end
  end

  def add k, v
    key = k.to_s
    return if @data.key?(key)
    @data[key] = v
    @added = true
  end

  def indexed_keys
    @data.keys.collect { |e| e.to_i }
  end

  def commit
    return unless @added
    open(@path, 'w') do |f|
      @data.each do |k,v|
        f.puts "#{k}#{@separator}#{v}"
      end
    end
    @added = false
    log 'Commited'
  end

  def log s
    puts "indx: #{s}"
  end
end

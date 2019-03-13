class API
  # Recursively gathers data about a block from the API
  def self.block_api block_index
    all = []
    next_page = "https://api.smartbit.com.au/v1/blockchain/block/#{block_index}?limit=1000"
    loop do
      break if next_page.nil?
      puts "curl: #{next_page}"
      out = `curl -sS '#{next_page}'`
      json = JSON.parse(out.strip)
      next_page = json['block']['transaction_paging']['next_link']
      all.push json
    end

    original = nil
    while !all.empty?
      original = all.pop if original.nil?
      next if all.empty?
      json = all.pop
      original['block']['transactions'].concat(json['block']['transactions'])
    end

    unless original.nil?
      original = original['block']
      original.delete('transaction_paging')
    end

    original
  end

  def self.next_block
    json = API.json_get('http://nnfee_harmony_1:5678/')
    json['last_block_index']
  end

  def self.save_mempool_to path
    `curl https://dedi.jochen-hoenicke.de/queue/mempool.log > #{path}`
  end

  def self.json_get url
    url = URI.parse(url)
    req = Net::HTTP::Get.new(url.to_s)
    res = Net::HTTP.start(url.host, url.port) {|http|
      http.request(req)
    }
    JSON.parse(res.body)
  end
end

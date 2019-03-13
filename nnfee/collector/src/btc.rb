class BTC
  def initialize url
    @url = url
  end

  def mk_request method, params=[]
    params = [params] unless params.is_a? Array
    hash = {
      jsonrpc: '1.0',
      id: Time.now.to_i.to_s,
      method: method,
      params: params
    }
    out = `curl -sS -d '#{hash.to_json}' -H 'content-type:text/plain;' '#{@url}'`
    JSON.parse(out.strip)['result']
  end

  def method_missing(name, *args)
    mk_request(name, *args)
  rescue ArgumentError => e
    puts "Argument error: #{name} #{args}"
    raise e
  end
end

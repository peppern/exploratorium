#!/usr/bin/env ruby

require 'rubygems'
require 'net/http'
require 'uri'

def search(query)
  query = query.split.join("+").gsub('"', '%22')
  uri = URI.parse("http://www.google.com/search?q=#{query}")
  return Net::HTTP.get_response(uri).body
end

def hits(query)
  # pattern = /Results <b>\d+<\/b> - <b>\d+<\/b> of (about )?<b>([\d,]+)<\/b>/
  pattern = /([\d,]+) results/
  results = search(query).match(pattern)
  return results ? results[1].gsub(/[^\d]/,'').to_i : 0
end

shows = <<END.split("\n")
Mad Men
Breaking Bad
Game of Thrones
END

scores = shows.map do |show|
  [show,
   hits("\"#{show} is the best show on TV\""),
   hits("\"#{show} is the best show on television\"")]
end
scores.sort! {|a, b| b[1] + b[2] <=> a[1] + a[2]}
puts scores.map {|s| s.join "\t"}.join "\n"

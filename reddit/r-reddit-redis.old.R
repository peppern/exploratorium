require('rredis')
redisConnect()
redisHGet("programming:2011-06-21:21", "the")

valFor <- function(subreddit, word, t) {
  datestamp = format(t, "%Y-%m-%d:%H")
  key = paste(subreddit, datestamp, sep=":")
  val = redisHGet(key, word)
  if (is.null(val)) {
    return(0)
  } else {
    return(as.numeric(val))
  }
}

vecFor <- function(subreddit, word, start, end, step) {
  vals = c()
  t = start
  while (t < end) {
    val = valFor(subreddit, word, t)
    vals = c(vals, val)
    t = t + step
  }
  return(vals)
}

# zipf plot
plot(sort(as.numeric(redisHVals("programming:2011-06-21:12")), decreasing=TRUE), log="xy")

start = Sys.time() - 7 * 24 * 60 * 60
end = Sys.time() - 14 * 60 * 60
step = 60 * 60

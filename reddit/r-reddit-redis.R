require('rredis')
redisConnect()

valFor <- function(subreddit, word, t) {
  datestamp = format(t, "%Y-%m-%d:%H")
  key = paste(subreddit, datestamp, sep=":")
  val = redisZScore(key, word)
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

start = Sys.time() - 15 * 24 * 60 * 60
end = Sys.time()
step = 60 * 60

# zipf plot
num = redisZCard("programming:2011-06-21:12")
wordcounts = redisZRange("programming:2011-06-21:12", 0, num, decreasing = TRUE, withscores = TRUE)
plot(as.matrix(wordcounts$scores), log="xy")

# foo vs bar
plot(vecFor("programming", "foo", start, end, step), type="l", col="red")
lines(vecFor("programming", "bar", start, end, step), col="blue")

# simple moving average
require('TTR')
plot(SMA(vecFor("programming", "d", start, end, step) / norm, 24), type="l", col="red")

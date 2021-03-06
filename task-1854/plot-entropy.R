library(ggplot2)
library(reshape)
library(scales)

p <- read.csv("prob-extracted.csv", header = FALSE,
  col.names = c("validafter", "minadvbw", "advbw", "cumprob", "prob"),
  stringsAsFactor = FALSE)
p <- p[p$minadvbw >= 20480, ]
c <- data.frame(x = p$advbw, y = p$cumprob,
  colour = as.factor(p$minadvbw))
ggplot(c, aes(x = x, y = y, colour = colour)) +
geom_line() +
scale_x_log10(name = "\nAdvertised bandwidth in B/s (log scale)") +
scale_y_continuous(name = "Cumulative probability\n") +
scale_colour_hue(name = "Adv. bw. cutoff in B/s") +
opts(title = paste("Consensus with valid-after time", max(p$validafter)),
  legend.position = "top")

ggplot(c, aes(x = x, y = y, colour = colour)) +
geom_line() +
scale_x_log10(name = "\nAdvertised bandwidth in B/s (log scale)") +
scale_y_log10(name = "Cumulative probability (log scale)\n") +
scale_colour_hue(name = "Adv. bw. cutoff in B/s") +
opts(title = paste("Consensus with valid-after time", max(p$validafter)),
  legend.position = "top")

p <- p[p$minadvbw == 20480 | p$minadvbw == 1048576, ]
c <- data.frame(x = p$advbw, y = p$prob,
  colour = as.factor(p$minadvbw))
ggplot(c, aes(x = x, y = y, colour = colour)) +
geom_point(alpha = 0.25) +
scale_x_log10(name = "\nAdvertised bandwidth in B/s (log scale)") +
scale_y_continuous(name = paste("Single relay probability, *not*",
  "probability distribution function\n")) +
scale_colour_hue(name = "Advertised bandwidth cutoff in B/s") +
opts(title = paste("Consensus with valid-after time", max(p$validafter)),
  legend.position = "top")

ggplot(c, aes(x = x, y = y, colour = colour)) +
geom_point(alpha = 0.25) +
scale_x_log10(name = "\nAdvertised bandwidth in B/s (log scale)") +
scale_y_log10(name = paste("Single relay probability, *not*",
  "probability distribution function (log scale)\n")) +
scale_colour_hue(name = "Advertised bandwidth cutoff in B/s") +
opts(title = paste("Consensus with valid-after time", max(p$validafter)),
  legend.position = "top")

c <- p[p$advbw >= 1048576, ]
c <- data.frame(advbw = c$advbw, prob = c$prob,
  minadvbw = paste("c", c$minadvbw, sep = ""))
c <- cast(c, advbw ~ minadvbw, value = "prob")
c <- data.frame(advbw = c$advbw, rel = c$c1048576 / c$c20480)
ggplot(c, aes(x = advbw, y = rel)) +
geom_point(alpha = 0.25) +
scale_x_log10(name = "\nAdvertised bandwidth in B/s (log scale)") +
scale_y_continuous(name = paste("Ratio of probaility at 1 MiB/s cutoff",
  "to probability at 20 KiB/s cutoff\n")) +
opts(title = paste("Consensus with valid-after time ", max(p$validafter),
  "\n", sep = ""), legend.position = "top")

e <- read.csv("linf-extracted.csv", header = FALSE,
  col.names = c("validafter", "min_adv_bw", "relays", "linf",
  "excl_adv_bw", "graph"), stringsAsFactor = FALSE)

l <- e[e$graph == 'last', ]
l <- data.frame(x = l$min_adv_bw, relays = l$relays,
  excladvbw = l$excl_adv_bw, linf = l$linf)
l <- melt(l, "x")
ggplot(l, aes(x = x, y = value)) +
geom_line() +
facet_grid(variable ~ ., scales = "free_y") +
scale_x_log10(name = "\nAdvertised bandwidth cutoff in B/s (log scale)") +
scale_y_continuous(name = paste("Number of relays, excluded advertised",
  "bandwidth, or linf\n")) +
opts(title = paste("Consensus with valid-after time ", max(e$validafter),
  "\n", sep = ""))

l <- e[e$graph == 'last', ]
l <- data.frame(x = l$min_adv_bw, relays = l$relays,
  excladvbw = l$excl_adv_bw, linf = l$linf)
l <- melt(l, "x")
ggplot(l, aes(x = x, y = value)) +
geom_line() +
facet_grid(variable ~ ., scales = "free_y") +
scale_x_log10(name = "\nAdvertised bandwidth cutoff in B/s (log scale)") +
scale_y_log10(name = paste("Number of relays, excluded advertised",
  "bandwidth, or linf (log scale)\n")) +
opts(title = paste("Consensus with valid-after time ", max(e$validafter),
  "\n", sep = ""))

l <- e[e$graph == 'last' & e$min_adv_bw >= 10000 & e$min_adv_bw <= 100000, ]
l <- data.frame(x = l$min_adv_bw, relays = l$relays,
  excladvbw = l$excl_adv_bw, linf = l$linf)
l <- melt(l, "x")
ggplot(l, aes(x = x, y = value)) +
geom_line() +
facet_grid(variable ~ ., scales = "free_y") +
scale_x_log10(name = "\nAdvertised bandwidth cutoff in B/s (zoomed, log scale)") +
scale_y_continuous(name = paste("Number of relays, excluded advertised",
  "bandwidth, or linf\n")) +
opts(title = paste("Consensus with valid-after time ", max(e$validafter),
  "\n", sep = ""))

h <- e[e$graph == 'history' & e$min_adv_bw == 10000, ]
h <- data.frame(validafter = h$validafter, relays = h$relays, linf = h$linf)
h <- aggregate(h[, 2:length(h)], by = list(x = as.Date(h$validafter)), FUN = mean)
h <- melt(h, "x")
ggplot(h, aes(x = as.POSIXct(x), y = value)) +
geom_line() +
facet_grid(variable ~ ., scales = "free_y") +
scale_x_datetime(name = "") +
scale_y_continuous(name = "") +
opts(title = "Advertised bandwidth cutoff 10000 B/s\n")

h <- e[e$graph == 'history' & e$min_adv_bw == 50000, ]
h <- data.frame(validafter = h$validafter, relays = h$relays, linf = h$linf)
h <- aggregate(h[, 2:length(h)], by = list(x = as.Date(h$validafter)), FUN = mean)
h <- melt(h, "x")
ggplot(h, aes(x = as.POSIXct(x), y = value)) +
geom_line() +
facet_grid(variable ~ ., scales = "free_y") +
scale_x_datetime(name = "") +
scale_y_continuous(name = "") +
opts(title = "Advertised bandwidth cutoff 50000 B/s\n")

h <- e[e$graph == 'history' & e$min_adv_bw == 100000, ]
h <- data.frame(validafter = h$validafter, relays = h$relays, linf = h$linf)
h <- aggregate(h[, 2:length(h)], by = list(x = as.Date(h$validafter)), FUN = mean)
h <- melt(h, "x")
ggplot(h, aes(x = as.POSIXct(x), y = value)) +
geom_line() +
facet_grid(variable ~ ., scales = "free_y") +
scale_x_datetime(name = "") +
scale_y_continuous(name = "") +
opts(title = "Advertised bandwidth cutoff 100000 B/s\n")

h <- e[e$graph == 'history' & e$min_adv_bw %in% c(10000, 50000, 100000), ]
h <- data.frame(validafter = h$validafter, min_adv_bw = h$min_adv_bw, relays = h$relays, linf = h$linf)
h <- aggregate(h[, 2:length(h)],
  by = list(x = as.Date(h$validafter), min_adv_bw = h$min_adv_bw), FUN = mean)
h <- melt(h, c("x", "min_adv_bw"))
ggplot(h, aes(x = as.POSIXct(x), y = value, colour = as.factor(min_adv_bw))) +
geom_line() +
facet_grid(variable ~ ., scales = "free_y") +
scale_x_datetime(name = "") +
scale_y_continuous(name = "") +
scale_colour_hue(name = "Advertised bandwidth cutoff in B/s") +
opts(legend.position = "bottom")

h <- e[e$graph == 'history' & e$min_adv_bw == 10000, ]
m10000 <- data.frame(linf = sort(h$linf),
  frac_cons = (1:length(h$linf))/length(h$linf), min_adv_bw = "10000")
h <- e[e$graph == 'history' & e$min_adv_bw == 50000, ]
m50000 <- data.frame(linf = sort(h$linf),
  frac_cons = (1:length(h$linf))/length(h$linf), min_adv_bw = "50000")
h <- e[e$graph == 'history' & e$min_adv_bw == 100000, ]
m100000 <- data.frame(linf = sort(h$linf),
  frac_cons = (1:length(h$linf))/length(h$linf), min_adv_bw = "100000")
h <- rbind(m10000, m50000, m100000)
ggplot(h, aes(x = linf, y = frac_cons, colour = as.factor(min_adv_bw))) +
geom_line() +
scale_x_continuous(name = "") +
scale_y_continuous(
  name = "Fraction of consensuses from 2011-11-01 to 2012-10-31\n") +
scale_colour_hue(name = "Advertised bandwidth cutoff in B/s") +
opts(legend.position = "bottom")


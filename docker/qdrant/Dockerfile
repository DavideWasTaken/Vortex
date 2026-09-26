FROM busybox:1.36.1-musl AS busybox

FROM qdrant/qdrant:v1.14.1

COPY --from=busybox /bin/busybox /busybox
RUN ["/busybox", "mkdir", "-p", "/usr/local/bin"]
RUN ["/busybox", "cp", "/busybox", "/usr/local/bin/busybox"]
RUN ["/usr/local/bin/busybox", "--install", "-s", "/usr/local/bin"]

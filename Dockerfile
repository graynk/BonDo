FROM maven:3.6.3-jdk-11 AS mvn

COPY pom.xml /
RUN mvn dependency:go-offline
COPY lib/JImageHash-3.0.0.jar /
RUN mvn install:install-file \
       -Dfile=JImageHash-3.0.0.jar \
       -DgroupId=com.github.kilianB \
       -DartifactId=JImageHash \
       -Dversion=3.0.0 \
       -Dpackaging=jar \
       -DgeneratePom=true
COPY src /src
#  --mount=type=cache,target=/root/.m2
RUN mvn package

FROM bellsoft/liberica-openjdk-alpine:11.0.7-10
COPY --from=mvn /target/lib /app
COPY --from=mvn /target/bondo-1.0.jar /app
COPY nesmeshno.ogg /app

WORKDIR /app
ENTRYPOINT ["java", "-jar", "bondo-1.0.jar"]
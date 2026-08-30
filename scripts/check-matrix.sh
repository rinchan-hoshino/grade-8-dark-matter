#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
for version in 1.21.1 26.1.2 26.2; do
  echo "== Grade 8 Dark Matter ${version} =="
  cd "$root/versions/$version"
  if [[ "$version" == 1.21.1 ]]; then
    /home/rin/.local/bin/rin-gradle ./gradlew clean test build
  else
    JAVA_HOME=/home/rin/.local/jdk-25 PATH=/home/rin/.local/jdk-25/bin:$PATH \
      /home/rin/.local/bin/rin-gradle ./gradlew clean test build
  fi
done

# beetle

Supporting tool for the ["mapping the void"](../README.md) analysis. Given a geth repo and a
snapshot, it builds two BAL arms, replays a block range.

```sh
uv run beetle verify --snapshot <dir> --range <from..to> --geth <geth-with-bal>
uv run beetle run    --repo <geth-root> --snapshot <dir> --range <from..to>
```

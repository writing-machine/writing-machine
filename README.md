# Writing Machine
A Machine that writes texts.
```bash
  echo '[{"role": "user", "content": "Write an explanatory text..."}]' \
    | uvx writing-machine \
        --provider-api-key=sk-ant-api... \
        --github-token=ghp_... \
        --mode=single
```
Or:
```bash
  pip install writing-machine
```
Then:
```Python
  # Python
  import writing_machine
```

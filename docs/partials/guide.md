## Configuring Semgrep

The Semgrep engine will run on all non-excluded files using an array of configs saved in your `.codeclimate.yml` file. The following is an example of what the `.codeclimate.yml` could look like:

### Sample CodeClimate Configuration

```yaml
---
engines:
  semgrep:
    enabled: true
    options:
      configs:
        - auto
        - p/ci
```

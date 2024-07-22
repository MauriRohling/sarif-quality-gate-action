# SARIF Quality Gate Check

A GitHub Action that checks the quality of your code using a [SARIF file](https://docs.oasis-open.org/sarif/sarif/v2.0/csprd02/sarif-v2.0-csprd02.html). It can be used to fail a build if the quality is below a certain threshold.

## Usage

To use this action, include the following step in your workflow file:

```yaml
- name: SARIF Quality Gate Check
    uses: maurirohling/sarif-quality-gate-action@v1
    with:
        sarif-file-path: path/to/SARIF
        max-errors: 0
        max-warnings: 5
```



## License

This action is licensed under the [MIT License](LICENSE).

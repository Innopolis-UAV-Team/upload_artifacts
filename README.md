# Artifact Uploader to our Local storage

The repository provides a GitHub Action step for uploading an artifact to a MINIO storage system on our local machine.

## Usage

:exclamation: **Important:** only works for our local runner currently.

1) Force running on our local machine:
    ```yaml
    build:
      runs-on: [self-hosted, StepanQGC]
    ```
2) Add the uploading step to your workflow (usually at the end):
    ```yaml
    steps:
      - name: Upload artifacts
        uses: Innopolis-UAV-Team/upload_artifacts@v1
        with:
          path: *my_file*
          MINIO_ACCESS_KEY: ${{ secrets.MINIO_ACCESS_KEY }}
          MINIO_SECRET_KEY: ${{ secrets.MINIO_SECRET_KEY }}
    ```
3) Replace `*my_file*` with the path to your file in the repository.
    > E.g. path to `test.yml` is `.github/workflows/test.yml`.
4) Get secrets for your repository from https://github.com/stepan14511 or https://github.com/AsiiaPine. Add them to the secrets of your repository. There is a possibility that you do not have enough permissions to do so, then ask someone responsible for this to do so.

    Guide how to add secrets: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository

    Secrets, you need to add:
    1) `MINIO_ACCESS_KEY`
    2) `MINIO_SECRET_KEY`

## Where to find artifacts, stored by this action

1) Go to the desired action.  

    You can do it right from the commit page, or from the `Actions` tab of your repository.

2) Open `build` job.
3) Find `Upload artifacts` step there.
4) You will find the links to your artifacts there.

    E.g.:
    ```yaml
    ----------FILE LOCATION----------
    VPN (Netherlands):     http://10.8.0.4:9001/browser/artifacts/upload_artifacts...
    WIFI (might change):   http://10.95.0.117:9001/browser/artifacts/upload_artifacts...
    ---------------------------------
    ```
5) Login with READONLY account:
    - Password: `uavteamgit`
    - Password: `drone123`

## Troubleshooting
<details>
<summary>Action is waiting for the runner infinitely long.</summary>

1) Call https://github.com/stepan14511 or https://github.com/AsiiaPine and tell them about the problem.

</details>

<details>
<summary>Action is failing</summary>

1) Check the logs there and ensure that the problem is not on your side.
2) Open an Issue and wait for the help.

</details>

<details>
<summary>Artifact link is not opening</summary>

1) Try the second link.
2) Check that you are connected to the `drone` or `drone_5G`.
3) Or check that you are connected to our VPN (`OpenVPN from Netherlands`, not any sort of Wireshark).
4) Ask https://github.com/stepan14511 or https://github.com/AsiiaPine if IP you have in the link is correct. If not, replace it with the correct one.
5) Open an Issue and wait for the help.
</details>

## Future

- [x] [Feature] Direct link to file.
- [ ] [Feature] Create separate bucket for storing releases.
- [ ] [Feature] Make users a choice of different types of artifacts (simple commit, release, stable version, etc.) to store them separately and treat the artifacts appropriately.
- [ ] [Feature] Upload several files at the same time.
- [ ] [Feature] Make access to the filebase from other runners (white IP is necessary for the filesystem).
- [ ] [Safety] Make the filesystem distributed.

> You are free to suggest any features in the `Issues` tab.
## License

This project is licensed under the MIT License.

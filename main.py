import subprocess as sp
import concurrent.futures
import re


# get connected wlans
def extract_wlans() -> list[str]:
    cmd = "netsh wlan show profile"
    o = sp.run(
        f"powershell {cmd}",
        shell=True,
        check=True,
        encoding="utf8",
        capture_output=True,
    ).stdout
    pattern = re.compile(r".Profile.+:.(.+)", re.IGNORECASE)
    return list(m.group(1) for m in pattern.finditer(o))


def get_keys(wlans: list[str]) -> zip:
    keys = []
    pattern = re.compile(r"Key Content.+:.(.+)", re.IGNORECASE)
    for wlan in wlans:
        cmd = f"netsh wlan show profile name='{wlan}' key=clear"
        o = sp.run(
            f"powershell {cmd}",
            check=True,
            shell=True,
            capture_output=True,
            encoding="utf8",
        ).stdout
        k = pattern.findall(o)
        keys.append(k[0] if len(k) > 0 else None)
    return zip(wlans, keys)


def write_to_file(z: zip, file: str = "wlan_keys.txt") -> None:
    kv = get_keys(extract_wlans())
    # cp to file
    for k, v in list(kv):
        cmd = f"powershell echo '{k} : {v}' >> {file}"
        sp.run(cmd)


if __name__ == "__main__":
    wlans = extract_wlans()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_keys, wlans)
        print("(WAIT!) Breaking WLANs...")
        return_value = future.result()
        write_to_file(return_value)
        print("Got It! ✔")

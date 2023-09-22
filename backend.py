from typing import Optional

from function import _req_post, _req_patch, _req_get


def prompt_create(bk: dict, name: str, content: list[dict]) -> Optional[dict]:
    """st.secrets.get("backend")"""
    data = {
        "name": name,
        "content": content,
    }
    rsp = _req_post(
        endpoint=bk['endpoint'],
        public_key=bk['public_key'],
        private_key=bk['private_key'],
        table='prompt',
        json_data={k: v for k, v in data.items() if v is not None}
    )
    if not rsp.ok:
        print(f"Error# prompt_create# name {name}, code {rsp.status_code}")
        return None
    return rsp.json()


def prompt_by(bk: dict, prompt_id: str) -> Optional[dict]:
    if prompt_id is None or prompt_id == "":
        return None
    rsp = _req_get(
        endpoint=bk['endpoint'],
        public_key=bk['public_key'],
        private_key=bk['private_key'],
        table='prompt',
        record_id=prompt_id,
    )
    if not rsp.ok:
        print(f"ERROR# prompt_by# id {prompt_id}, code {rsp.status_code}")
        return None
    data = rsp.json()
    return data


def prompt_patch(bk: dict, prompt_id: str,
                 prompt_name: Optional[str] = None,
                 prompt_content: Optional[list[dict]] = None,
                 ):
    data = {
        "name": prompt_name,
        "content": prompt_content,
    }
    data = {key: value for key, value in data.items() if value is not None}
    # print("debug prompt_update #", data)
    rsp = _req_patch(
        endpoint=bk['endpoint'],
        public_key=bk['public_key'],
        private_key=bk['private_key'],
        table='prompt',
        record_id=prompt_id,
        json_data={k: v for k, v in data.items() if (v is not None or v != "")}
    )
    if not rsp.ok:
        print(f"Error# prompt_patch# id {prompt_id}, code {rsp.status_code}")
        return None
    return rsp.json()
    pass


def prompt_list(bk: dict, name: str) -> list[dict]:
    rsp = _req_get(
        endpoint=bk['endpoint'],
        public_key=bk['public_key'],
        private_key=bk['private_key'],
        table='prompt',
        record_id=name,
        json_data={"name": name}
    )
    if not rsp.ok:
        print(f"Error# prompt_list# id {name}, code {rsp.status_code}")
        return []
    return rsp.json()
    pass

"""ReSync authentication."""
from __future__ import annotations

import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)
API_CORP_ID = "1007d2ad150c4000"
API_LOGIN = "https://api.gelighting.com/v2/user_auth"
API_REQUEST_TOKEN = "https://api.gelighting.com/v2/two_factor/email/verifycode"
API_VERIFY_TOKEN = "https://api.gelighting.com/v2/user_auth/two_factor"


class AuthError(Exception):
    pass


class UsernameError(AuthError):
    pass


class TwoFactorRequiredError(AuthError):
    pass


async def cync_check_user(username) -> bool:
    """TODO The real login sequence API isn't as implemented.

    Looking at the other implementation and sniffing the website, it looks like
    GE actually just uses 404 for "no such account". The actual authentication
    step is password and 2FA in one shot to get the token.
    """
    raise NotImplementedError


async def cync_authenticate(username, password):
    req = {
        "corp_id": API_CORP_ID,
        "email": username,
        "password": password,
    }

    async with aiohttp.ClientSession() as s, s.post(API_LOGIN, json=req) as resp:
        _LOGGER.debug("Auth response %s", resp)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            raise UsernameError("Invalid username")
        if resp.status == 400:
            body = await resp.json()
            _LOGGER.debug("Auth 400 body %s", body)
            raise TwoFactorRequiredError("Must include a token")

        raise Exception("Unexpected response", resp)


async def cync_verify_token(username, password, token):
    req = {
        "corp_id": API_CORP_ID,
        "email": username,
        "password": password,
        "two_factor": token,
        "resource": "abcdefghijklmnop",
    }

    async with aiohttp.ClientSession() as session, session.post(
        API_VERIFY_TOKEN, json=req
    ) as resp:
        _LOGGER.debug("Token response %s", resp)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 400:
            body = await resp.json()
            if "error" in body:
                raise AuthError(body["error"])
        raise AuthError("Unexpected response", resp)


class ReCyncSession:
    """Cync authentication session wrapper."""

    def __init__(self, credentials=None) -> None:
        self._credentials = credentials or {}
        self._username = None

    async def authenticate(self, username, password, token=None):
        """Authenticate with the API and get a token."""
        if token is None:
            self._credentials = await cync_authenticate(username, password)
        else:
            self._credentials = await cync_verify_token(username, password, token)
        return self._credentials

    async def request_code(self, username):
        """Request a token via email."""
        request_code_data = {
            "corp_id": API_CORP_ID,
            "email": username,
            "local_lang": "en-us",
        }
        async with aiohttp.ClientSession() as s, s.post(
            API_REQUEST_TOKEN, json=request_code_data
        ) as resp:
            _LOGGER.debug("Token request response %s", resp)
            if resp.status != 200:
                raise AuthError("Unexpected status", resp)

    @property
    def user_id(self):
        return self._credentials["user_id"]

    @property
    def access_token(self):
        return self._credentials["access_token"]

    @property
    def binary_token(self):
        "Binary version of the login code."
        login_code = (
            bytearray.fromhex("13000000")
            + (10 + len(self._credentials["authorize"])).to_bytes(1, "big")
            + bytearray.fromhex("03")
            + self._credentials["user_id"].to_bytes(4, "big")
            + len(self._credentials["authorize"]).to_bytes(2, "big")
            + bytearray(self._credentials["authorize"], "ascii")
            + bytearray.fromhex("0000b4")
        )
        return [int.from_bytes([byt], "big") for byt in login_code]

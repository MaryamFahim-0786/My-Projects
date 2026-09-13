import Cookies from "js-cookie";

export function storeTokens(access_token: string, refresh_token: string) {
  Cookies.set("access_token", access_token, { expires: 1 / 24, sameSite: "strict" });
  Cookies.set("refresh_token", refresh_token, { expires: 7, sameSite: "strict" });
}

export function clearTokens() {
  Cookies.remove("access_token");
  Cookies.remove("refresh_token");
}

export function isAuthenticated(): boolean {
  return Boolean(Cookies.get("access_token"));
}

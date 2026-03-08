import { getUser } from "../../application/get_user"

export async function fetchOverHttp(store: unknown, id: string) {
  return getUser(store as never, id)
}

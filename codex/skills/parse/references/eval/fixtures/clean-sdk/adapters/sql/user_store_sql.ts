import type { UserStore } from "../../ports/user_store"
import type { User } from "../../domain/user"

export const sqlUserStore: UserStore = {
  async load(id: string): Promise<User> {
    return { id }
  },
}

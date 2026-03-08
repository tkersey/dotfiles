import type { User } from "../domain/user"

export interface UserStore {
  load(id: string): Promise<User>
}

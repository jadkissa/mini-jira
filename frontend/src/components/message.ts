export function message(err: unknown) {
  return err instanceof Error ? err.message : 'Could not reach the API'
}

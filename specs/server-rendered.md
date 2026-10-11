# Server-rendered contract

Applies to all `*-ssr-*` examples.

## Flows

1. **View list:** `GET /` returns `200` with an HTML page listing all items.
2. **Add:** submit the add form (`POST /todos` with a `title` field) redirects back to `/` and the new item appears.
3. **Toggle:** submit the per-item toggle form (`POST /todos/{id}/toggle`) redirects back to `/` with the item's state flipped.
4. **Delete:** submit the per-item delete form (`POST /todos/{id}/delete`) redirects back to `/` without the item.

Method and path details stay idiomatic (e.g. Django URL names), but the four user-visible flows above must work.

## Page content

- The page shows every item's title and its done/not-done state.
- The page contains an add form, plus one toggle and one delete control per item.
- Visual styling is not compared; textual content and controls are.

## Form behavior

- Successful submissions use POST-redirect-GET back to `/`.
- Empty titles are rejected: the list re-renders with an error message and no item is created.
- Unknown ids answer `404`.

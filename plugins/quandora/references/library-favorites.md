# Factor and Strategy Library Favorites

Use `set_library_item_favorite` with `scope` (`factors` or `strategies`), the exact canonical
`item_id`, and explicit `favorite: true|false`. The server persists the same user metadata read
by the frontend. Repeating a value is idempotent; failed writes do not count as success.
Use `list_library_folder_items` with the same scope and optional `favorite` filter to read stars.

Favorites are independent of folders. Starring does not move, duplicate, revise or backtest an
item, and an item can remain both starred and in a folder. Use only exact owned identities;
resolve ambiguous legacy identities instead of guessing. Existing folder CRUD and placement
operations keep their revision/concurrency requirements. Public Portfolio favorites use
`set_portfolio_favorite` in the Strategy Portfolio skill, not this LibraryFolder scope.

"""Basic board creation examples.

These examples demonstrate creating and managing boards (dashboards).
"""

from __future__ import annotations

from honeycomb import Board, BoardCreate, HoneycombClient


# start_example:create_board
async def create_basic_board(client: HoneycombClient) -> str:
    """Create a basic service overview board.

    Args:
        client: Authenticated HoneycombClient

    Returns:
        The created board ID
    """
    board = await client.boards.create_async(
        BoardCreate(
            name="Service Overview",
            description="Key metrics for the API service",
            type="flexible",
        )
    )
    return board.id


# end_example:create_board


# start_example:list_boards
async def list_boards(client: HoneycombClient) -> list[Board]:
    """List all boards in the environment.

    Args:
        client: Authenticated HoneycombClient

    Returns:
        List of boards
    """
    boards = await client.boards.list_async()
    for board in boards:
        print(f"{board.name}: {board.type} type")
    return boards


# end_example:list_boards


# start_example:get
async def get_board(client: HoneycombClient, board_id: str) -> Board:
    """Get a specific board by ID.

    Args:
        client: Authenticated HoneycombClient
        board_id: ID of the board to retrieve

    Returns:
        The board object
    """
    board = await client.boards.get_async(board_id)
    print(f"Name: {board.name}")
    print(f"Description: {board.description}")
    print(f"Type: {board.type}")
    return board


# end_example:get


# start_example:update
async def update_board(client: HoneycombClient, board_id: str) -> Board:
    """Update a board's name and description.

    Args:
        client: Authenticated HoneycombClient
        board_id: ID of the board to update

    Returns:
        The updated board
    """
    # Get existing board first to preserve values
    existing = await client.boards.get_async(board_id)

    # Update with new values
    updated = await client.boards.update_async(
        board_id,
        BoardCreate(
            name="Updated Service Overview",
            description="Updated: Key metrics for the API service",
            type=existing.type,
        ),
    )
    return updated


# end_example:update


# start_example:delete
async def delete_board(client: HoneycombClient, board_id: str) -> None:
    """Delete a board.

    Args:
        client: Authenticated HoneycombClient
        board_id: ID of the board to delete
    """
    await client.boards.delete_async(board_id)


# end_example:delete


# start_example:list_sync
def list_boards_sync(client: HoneycombClient) -> list[Board]:
    """List boards using sync client.

    Args:
        client: Authenticated HoneycombClient

    Returns:
        List of boards
    """
    boards = client.boards.list()
    for board in boards:
        print(f"{board.name}")
    return boards


# end_example:list_sync


# TEST_ASSERTIONS
async def test_create_board(client: HoneycombClient, board_id: str) -> None:
    """Verify the example worked correctly."""
    board = await client.boards.get_async(board_id)
    assert board.name == "Service Overview"
    assert board.type == "flexible"


async def test_list_boards(boards: list[Board]) -> None:
    """Verify list example worked correctly."""
    assert isinstance(boards, list)


async def test_get_board(board: Board, expected_board_id: str) -> None:
    """Verify get example worked correctly."""
    assert board.id == expected_board_id
    assert board.name is not None


async def test_update_board(updated: Board, original_board_id: str) -> None:
    """Verify update example worked correctly."""
    assert updated.id == original_board_id
    assert updated.name == "Updated Service Overview"
    assert "Updated:" in updated.description


# CLEANUP
async def cleanup(client: HoneycombClient, board_id: str) -> None:
    """Clean up resources created by example."""
    await delete_board(client, board_id)

Getting started
----------------------

**Here's basic bot code**

.. highlight:: python
    :linenothreshold: 5

.. code-block:: python

    from quant import Client, InteractionContext, SlashCommand

    client = Client(token="Bot <YOUR TOKEN HERE>")


    async def slash_command_callback(context: InteractionContext) -> None:
        await context.interaction.respond(content="Pong!")

    if __name__ == "__main__":
        ping_command = SlashCommand(
            name="ping",
            description="Based ping command"
        )
        ping_command.set_callback(slash_command_callback)
        client.add_slash_command(ping_command)

        client.run()
        # or
        client.run_autoshard()
        # or
        client.run_with_shards(5)


"""
Main
"""
import collections
import os
import re
import sqlite3
import discord

ANIMAL_CROSSING_CHANNEL_ID = '384952296183824384'

client = discord.Client()
friend_codes = []
conn = sqlite3.connect('ac.db')

FriendCode = collections.namedtuple('FriendCode', ['discord_id', 'discord_name',
                                                   'animal_crossing_name', 'friend_code'])

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print('Loading table...')
    load_list()

def load_list():
    c = conn.cursor()
    c.execute("SELECT * FROM `friend_codes`")

    for code in c.fetchall():
        friend_codes.append(FriendCode(*code))
    
    print('Done!')

@client.event
async def on_message(message):
    if message.channel.id == ANIMAL_CROSSING_CHANNEL_ID and message.content.startswith('!'):
        split = message.content[1:].split(' ')
        await parse_message(message.channel, message.author, split[0], ' '.join(split[1:]))


async def parse_message(channel, author, command, content):
    if command in COMMANDS:
        await COMMANDS[command](channel, author, content)
    else:
        await client.send_message(channel, 'Invalid command!')


async def add_friend_code(channel, author, content):
    """Adds a friend code to the friend_codes.txt"""
    split = content.split(' ')
    if len(split) < 2:
        await client.send_message(channel,
            'Invalid command format. Use: *!fc [Pocket Camp Username] [Friend Code]*')
        return

    username = split[0]
    friend_code = re.sub(r'\D', '', ''.join(split[1:]))

    if len(friend_code) < 11:
        await client.send_message(channel, 'Invalid friend code. Use: *!fc [Pocket Camp Username] [Friend Code]*')
        return

    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO `friend_codes` (`discord_id`, `discord_name`, `animal_crossing_name`, `friend_code`) VALUES (?, ?, ?, ?)",
                (author.id, author.name, username, friend_code))
    conn.commit()

    found = [i for i, code in enumerate(friend_codes) if code.discord_id == author.id]
    if not found:
        friend_codes.append(FriendCode(discord_id=author.id, discord_name=author.name, 
                                    animal_crossing_name=username, friend_code=friend_code))
        await client.send_message(channel, '<@{}> Added friend code!'.format(author.id))
    else:
        friend_codes[found[0]] = friend_codes[found[0]]._replace(friend_code=friend_code)
        await client.send_message(channel, '<@{}> Updated friend code!'.format(author.id))


async def print_friends(channel, author, content):
    if not friend_codes:
        await client.send_message(channel, 'I have no friends. Use: *!fc [Pocket Camp Username] [Friend Code]*')
        return

    longest_name = max([len(friend.discord_name) for friend in friend_codes] +
                   [len('Discord Name')]) + 2
    longest_ac_name = max([len(friend.animal_crossing_name) for friend in friend_codes] + 
                   [len('Animal Crossing Name')]) + 2

    message = '```'
    message += '┌{}┬{}┬{}┐\n'.format('─' * longest_name,
                                     '─' * longest_ac_name, 
                                     '─' * 15)
    message += '│{:^{longest_name}}│{:^{longest_ac_name}}│{:^15}│\n'.format(
        'Discord Name', 'Animal Crossing Name', 'Friend Code', longest_name=longest_name,
        longest_ac_name=longest_ac_name)
    message += '├{}┼{}┼{}┤\n'.format('─' * longest_name,
                                     '─' * longest_ac_name,
                                     '─' * 15)

    for friend in friend_codes:
        message += '│{:^{longest_name}}│{:^{longest_ac_name}}│{:^15}│\n'.format(
            friend.discord_name, friend.animal_crossing_name, friend.friend_code[:4] + ' ' + \
            friend.friend_code[4:8] + ' ' + friend.friend_code[8:], longest_name=longest_name,
            longest_ac_name=longest_ac_name)

    message += '└{}┴{}┴{}┘'.format('─' * longest_name,
                                   '─' * longest_ac_name,
                                   '─' * 15)
    message += '```'

    embed = discord.Embed(
        title='Pocket Camp Friend Codes',
        description=message,
        color=discord.Color.green()
    )

    await client.send_message(channel, embed=embed)
     
async def print_help(channel):
    await client.send_message(channel, 'Add your friend code with: *!fc [Pocket Camp Username] [Friend Code]*')
    await client.send_message(channel, 'Print friend codes with: *!friends*')

def main():
    """main"""
    client.run(os.environ['DISCORD_BOT_TOKEN'])


COMMANDS = {
    'fc': add_friend_code,
    'friends': print_friends,
    'help': print_help
}

if __name__ == '__main__':
    main()

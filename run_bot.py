"""
    REDDIT USER SIMULATOR -- this script will simulate my personal reddit account by posting comments and submissions
                             in subreddits that I frequent. It will do this by creating Markov chains from the comments
                             and posts I've made in the past.

    By Eli Anderson

    Ideas -- * make keys three words instead of two?
             * If the bot decides to post a submission, give it a random chance of it being a link post
             * If someone replies to bot, reply back to them?
"""

# built-in libraries
from collections import Counter
import os
import random
import time

# 3rd party libraries
import praw
from textblob import TextBlob

# Login the bot into reddit

def authenticate() :
    print('Authenticating...')
    reddit = praw.Reddit(client_id='0rXzDRFz76Wqkg',
                         client_secret='yO998bCXh0WfxhnE1hEx4PT6jk8',
                         user_agent='user_simulator v0.1',
                         username='_user_simulator_',
                         password='elephantsanddonkeysgrowbigears')
    print('Authenticated as ' + str(reddit.user.me()))
    return reddit

def generate_chain(text, chain) :
    print('Constructing chain...')
    words = text.split(' ')

    # the first word will be the key, and the subsequent word (index 1) will be the value
    idx = 1

    for word_value in words[idx+1:] :
        # to have decent coherency, each key will be two words -- e.g. in the 1st loop, key will be 'words[0] words[1]'
        key = words[idx-1] + ' ' + words[idx]

        # if a key is already in the chain, add word_value to the key's value, which is a list
        if key in chain and word_value not in chain[key]:
            chain[key].append(word_value)

        # if key isn't already in the chain, create that key and create a value list for it
        elif '\n' not in key :
            chain[key] = [word_value]

        idx += 1
    print('Chain constructed!')
    print(chain)
    return chain

def generate_comment(chain, starting_word) :
    print('Generating comment...')
    char_limit = 350

    while True :
        # generate the first word -- the code will continue only if it is valid
        word1 = starting_word
        p_o_s = ''
        print('Word: ' + word1)
        try :
            p_o_s = TextBlob(word1).tags[0][1]
            break
        except IndexError :
            print('Invalid word. Choosing a different one...')
            post_comment(chain)
    print(word1)
    # find a key that the first word belongs to and set word1 to that key
    key_list = []
    for key in chain.keys() :
        if key.split(' ')[0] == word1 :
            key_list.append(key)
    print('Key list: ' + str(key_list))
    word1 = random.choice(key_list)

    message = word1.capitalize()
    print('First two words: ' + message)
    # subtract 10 from char_limit since there'll need to be room for the last word if necessary
    while len(message) < (char_limit - 10) :

        # if word1 doesn't already have two words, add the word before word1
        if len(word1.split(' ')) < 2 :
            word1 = message.split(' ')[len(message.split(' '))-2] + ' ' + word1

        word2 = ''
        # choose the next word; if word1 isn't in chain's keys, then regenerate the message
        try :
            word2 = random.choice(chain[word1])
        except KeyError :
            print('\'' + word1 + '\' was not in the chain. Regenerating message...')
            return post_comment(chain)

        print(str(chain[word1]))
        # add code here to choose the most common value for word2 if the messages don't seem to be coherent enough
        print('Chosen word: ' + word2)

        # add word2 to the message
        message += ' ' + word2
        print('Message: ' + message)

        # set word1 to word2, allowing the while loop to continue adding to the message
        word1 = word2

        # sometimes word2 will be '' and that causes an IndexError with textbubble
        while True :
            try :
                p_o_s2 = TextBlob(word2).tags[0][1]
                break
            except IndexError :
                print('Invalid word. Regenerating comment...')
                return generate_comment(chain, starting_word)

        i = random.randint(0, 4)
        # 1 in 5 chance to end the message after 25 chars if word2 has punctuation
        if (word2[len(word2)-1] == '.' or word2[len(word2)-1] == '?' or word2[len(word2)-1] == '!') and len(message) >= 25 and i == 0 and p_o_s2 != 'CC' \
                and p_o_s2 != 'TO' and p_o_s2 != 'MD' and p_o_s2 != 'IN' and p_o_s2 != 'DT' and p_o_s2 != 'PDT':
            return message

        # if the message is getting close to the char limit and word2's part of speech makes sense to end on, add some
        # punctuation and return it
        if len(message) > (char_limit - 20) and p_o_s2 != 'CC' and p_o_s2 != 'TO' and p_o_s2 != 'MD' and p_o_s2 != 'IN'\
                and p_o_s2 != 'DT' and p_o_s2 != 'PDT':
            message += '.'
            print('Final message: ' + message)
            return message

    # catch-all if for some reason the previous if statements don't work
    message += '.'
    print('Final message: ' + message)
    return message

def generate_title(chain) :
    print('Generating submission title...')
    print(chain)
    char_limit = 50

    while True :
        # generate the first word -- the code will continue only if it is valid
        word1 = random.choice(list(chain.keys()))
        word1 = word1.split(' ')[0]
        p_o_s = ''
        print('Word: ' + word1)
        try :
            p_o_s = TextBlob(word1).tags[0][1]
        except IndexError :
            print('Invalid word. Choosing a different one...')

        if p_o_s != 'CC' and p_o_s != 'TO' and p_o_s != 'MD' and p_o_s != 'IN' :
            break
        else :
            print('Unacceptable part of speech. Choosing different word...')

    for key in chain.keys() :
        if key.split(' ')[0] == word1 :
            word1 = key

    message = word1.capitalize()
    print('First two words: ' + message)

    while len(message) < (char_limit - 10) :

        # if word1 doesn't already have two words, add the word before word1
        if len(word1.split(' ')) < 2 :
            word1 = message.split(' ')[len(message.split(' '))-2] + ' ' + word1

        word2 = ''
        # choose the next word; if word1 isn't in chain's keys, then regenerate the message
        try :
            word2 = random.choice(chain[word1])
        except KeyError :
            print('\'' + word1 + '\' was not in the chain. Regenerating message...')
            return generate_title(chain)

        print(str(chain[word1]))
        # add code here to choose the most common value for word2 if the messages don't seem to be coherent enough
        print('Chosen word: ' + word2)

        # add word2 to the message
        message += ' ' + word2
        print('Message: ' + message)

        # set word1 to word2, allowing the while loop to continue adding to the message
        word1 = word2

        p_o_s2 = TextBlob(word2).tags[0][1]
        i = random.randint(0, 2)
        # 1 in 3 chance to end the message after 50 chars if word2 has punctuation
        if (word2[len(word2)-1] == '.' or word2[len(word2)-1] == '?' or word2[len(word2)-1] == '!') and i == 0 and p_o_s2 != 'CC' \
                and p_o_s2 != 'TO' and p_o_s2 != 'MD' and p_o_s2 != 'IN' and p_o_s2 != 'DT' and p_o_s2 != 'PDT':
            return message

        # if the message is getting close to the char limit and word2's part of speech makes sense to end on, add some
        # punctuation and return it
        if len(message) > (char_limit - 10) and p_o_s2 != 'CC' and p_o_s2 != 'TO' and p_o_s2 != 'MD' and p_o_s2 != 'IN'\
                and p_o_s2 != 'DT' and p_o_s2 != 'PDT':
            print('Final message: ' + message)
            return message

    print('Final title: ' + message)

    return message


def post_comment(chain) :
    # randomly decide which subreddit to post the comment to
    subreddits = list(reddit.user.subreddits(limit=None))
    subreddit = random.choice(subreddits).display_name

    # randomly decide which submission to comment on -- to be valid, it must have a score greater than 300
    submissions = []

    for submission in reddit.subreddit(subreddit).hot(limit=50) :
        if submission.score > 300:
            submissions.append(submission)
    # include 50 submissions from /r/all
    for submission in reddit.subreddit('all').hot(limit=50) :
        # all submission will have plenty of discussion, so no need to filter any out
        submissions.append(submission)

    # if there are no 'hot' submissions in the chosen subreddit, choose a different one and try again
    # BTW -- Python registers empty sequences as false, so this is the fastest way to check for an empty list
    if not submissions :
        print('No submissions with a score greater than 300. Refreshing...')
        post_comment(chain)

    chosen_submission = random.choice(submissions)
    print('Posting comment in /r/' + chosen_submission.subreddit.display_name)
    print('Chosen submission title: ' + chosen_submission.title)
    print('Submission url: ' + chosen_submission.shortlink)

    # choose a common noun/adjective/verb in the submission's thread and use that as the first word in the message

    # remove any MoreComments objects
    chosen_submission.comments.replace_more()
    # create a CommentForest instance
    comments = chosen_submission.comments.list()
    comment = random.choice(comments)
    comment_bodies = [comment.body.replace('\n', '. ') for comment in comments]
    print(comment_bodies)
    words = ' '.join(comment_bodies)

    # add the words from the comments to the already existing markov chain of my own comments
    chain = generate_chain(words, chain)

    # put the words into a list for the counter
    words = words.split(' ')
    counter = Counter(words)
    print(counter.most_common(50))
    starting_word = ''
    while True:
        starting_word = random.choice(counter.most_common(50))[0]
        try :
            # starting word should only be acceptable if it is long enough (isn't a filler word)
            if len(starting_word) > 4:
                break
        except IndexError :
            print('Invalid word. Choosing a different one...')
    # there's a 1 in 5 chance of the comment being a reply to the submission/one of the forest comments respectively
    i = random.randint(0, 4)
    if i != 0 and chosen_submission.id not in submissions_replied_to :

        comment = generate_comment(chain, starting_word)
        if chosen_submission.id not in submissions_replied_to :
            try :
                chosen_submission.reply(comment)
            except :
                print('Comment was NOT posted.')

        # add submission ID to that list
        submissions_replied_to.append(chosen_submission.id)

        # save it to the .txt file for the next time the program runs
        with open('submissions_replied_to.txt', 'a') as file:
            file.write(chosen_submission.id + '\n')

    # only reply to comments if there are a sufficient amount
    elif chosen_submission.comments.__len__() > 50 and len(comment.body.split(' ')) > 10 :
        chosen_submission.comments.replace_more()
        print('Replying to another user...')
        print('User\'s comment: ' + comment.body)
        comment_thread = []
        # get all the comments from the comment thread you're replying to
        for second_level_comment in comment.replies :
            comment_thread.append(second_level_comment.body)
        print(comment_thread)
        reply_counter = Counter((' '.join(comment_thread)).split(' '))
        print(reply_counter.most_common(50))

        # if the OP comment has replies (the list isn't empty), choose a starting word from the replies
        # other wise choose a starting word from the OP comment instead
        while comment_thread :
            starting_word = random.choice(reply_counter.most_common(50))[0]
            # starting word should only be acceptable if it is long enough (isn't a filler word)
            if len(starting_word) > 4 :
                break
        while True :
            starting_word = random.choice(comment.body.split(' '))
            if len(starting_word) > 4 :
                break

        print(starting_word)
        message = generate_comment(chain, starting_word)

        # check if the comment was already replied to
        if comment.id not in comments_replied_to :
            try :
                comment.reply(message)
            except :
                print('Comment was NOT posted.')

        print('Replied to comment ' + comment.id)
        comments_replied_to.append(comment.id)
        with open('comments_replied_to.txt', 'a') as file:
            file.write(comment.id + '\n')

    # if no comments, just reply to the submission. This'll probably never happen tho
    elif chosen_submission.id not in submissions_replied_to :
        message = generate_comment(chain, starting_word)
        try:
            chosen_submission.reply(message)
        except:
            print('Comment was NOT posted.')
        submissions_replied_to.append(chosen_submission.id)
        with open('submissions_replied_to.txt', 'a') as file:
            file.write(chosen_submission.id + '\n')

def post_submission(title, body) :
    # randomly decide which subreddit to post the comment to
    subreddits = list(reddit.user.subreddits(limit=None))
    subreddit = random.choice(subreddits).display_name
    print('Posting submission in /r/' + subreddit)

    reddit.subreddit(subreddit).submit(title, body)

    print('Post submitted!')

    # add comment to the submission so that mods know a bot posted it
    # get the submission from bot's post history
    submission = reddit.redditor('_user_simulator_').submissions.new(limit=1)
    print('Submission url: ' + submission.shortlink)
    submission.reply('^(^This ^post ^was ^submitted ^automatically ^by ^a ^bot. ^Please ^PM ' +
                     '^this ^account ^if ^you ^take ^issue ^or ^have ^any ^suggestions.)')

    # add submission ID to that list
    submissions_replied_to.append(submission.id)

    # save it to the .txt file for the next time the program runs
    with open('submissions_replied_to.txt', 'a') as file:
        file.write(submission.id + '\n')


def run_bot(reddit, comments_replied_to, submissions_replied_to) :
    # clear the txt files so the program adds any new comments/submissions to them
    open('user_comments.txt', 'w').close()
    open('user_submissions.txt', 'w').close()

    # Loop through both of my accounts' comment/submission history and form a Markov dictionaries from them
    print('Reading comments and submissions...')
    for comment in reddit.redditor('_pony_slaystation_').comments.new(limit=None) :

        # Write all of the user's comments to user_comments.txt
        with open('user_comments.txt', 'a') as file:
            try :
                body = comment.body.replace('\n', '. ')
                file.write(body + '\n')
            except UnicodeError :
                print('Comment contained non UTF-8 chars; discarded.')

    for comment in reddit.redditor('moldyxorange').comments.new(limit=None):
        with open('user_comments.txt', 'a') as file:
            try :
                body = comment.body.replace('\n', '. ')
                file.write(body + '\n')
            except UnicodeError :
                print('Comment contained non UTF-8 chars; discarded.')

    for submission in reddit.redditor('_pony_slaystation_').submissions.new(limit=None) :
        with open('user_submissions.txt', 'a') as file :
            try :
                file.write(submission.title + '\n')
            except UnicodeError:
                print('Title contained non UTF-8 chars; discarded.')

    for submission in reddit.redditor('moldyxorange').submissions.new(limit=None) :
        with open('user_submissions.txt', 'a') as file :
            try :
                file.write(submission.title + '\n')
            except UnicodeError:
                print('Title contained non UTF-8 chars; discarded.')
    print('Finished!')

    # Generate a comment and submission title chain
    comments = ''
    with open('user_comments.txt', 'r') as file :
        comments = file.read()
    titles = ''
    with open('user_submissions.txt', 'r') as file :
        titles = file.read()

    comment_chain = generate_chain(comments, {})
    title_chain = generate_chain(titles, {})

    # 1 in 25 chance to post a submission instead of a comment
    i = random.randint(0, 24)
    if i == 0 :
        # Generate a submission title using title_chain
        title = generate_title(title_chain)
        # Generate the body of the submission using comment_chain and a random word from the title
        body = generate_comment(comment_chain, random.choice(title.split(' ')))
        # post dat submission
        post_submission(title, body)
    else :
        # post dat comment
        post_comment(comment_chain)

    print('Sleeping for 15 minutes...')
    time.sleep(60*15)

# Save the comments that have been replied to in the past so the bot doesn't reply to same comments the after each time
# it is run
#
# Uses .txt file to store the comment IDs


def get_saved_comments() :

    # If .txt file with comment IDs doesnt exist, create one and return a blank array

    if not os.path.isfile('comments_replied_to.txt') :
        comments_replied_to = []

    else :
        with open('comments_replied_to.txt', 'r') as file :

            # Read contents of the file
            comments_replied_to = file.read()

            # split() by new line
            comments_replied_to = comments_replied_to.split('\n')

    return comments_replied_to

def get_saved_submissions() :

    if not os.path.isfile('submissions_replied_to.txt') :
        submissions_replied_to = []

    else :
        with open('submissions_replied_to.txt', 'r') as file :
            submissions_replied_to = file.read()
            submissions_replied_to = submissions_replied_to.split('\n')

    return submissions_replied_to
reddit = authenticate()

# To prevent spam, create list of comment/submission IDs already replied to

comments_replied_to = get_saved_comments()
submissions_replied_to = get_saved_submissions()

# To automatically reply to comments, a while loop is used

while True :
    run_bot(reddit, comments_replied_to, submissions_replied_to)

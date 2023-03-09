Assumptions for channels.py
1. Channels_list_v1() and channels_listall_v1() lists channels in the order that they are created.
2. Channel_list functions contains show both public and private channels.
3. If the auth_user_id is not part of any channels, the channel_list will return an empty value.

Assumptions for auth.py
1. First and last names can contain special characters and could also be empty strings.
2. Emails don't need to have valid domain, just has to satisfy regular expression.

Assumptions for channel.py
1. Channel_detail_v1() lists owners and members in the order that they joined the channel. 
2. Assume users cannot invite themselves to the channel.
3. The parameter for channels_messages, "start" is a non negative integer. 

 
Iteration 2

Assumption for handle strings (*)
1. Handle string for a user can be purely numeric.
e.g A user with first name '1' and last name '2' will have handle string '12'.
2. Handle strings can also be empty.
e.g A user with first name '@' and last name '!' will have handle string ''.

Assumptions for dm.py
1. dm_list_v1 lists DMs in the order they are created
2. When sorting handles to generate DM name, the following rules apply:
- empty handles are listed first
- the order of precedence for digits is 0 - 9 that is, 0 precedes 1, 1 precedes 2....
- All digits precedes letters
e.g If users with handle '', '1simon' and '2simon' joinds a DM, the DM's name is 
', 1simon, 2simon'

Assumption for user.py
1. The token taken in is always correct and valid
2. No AccessErrors for all user functions so no need to import AccessError
3. Both user and users dictionary should not contain password 
4. Both user and users returned by user_all_v1 and user_profile_v1 are lists
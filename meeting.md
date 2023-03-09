Iteration 1

24th Sep  
Duration: 1 hour

    1. Delegating tasks to all members in the group through the use of GitLab Issue Board.
    2. Discussed how we would store all data in data store and asked tutor for verification.

29th Sep
Duration: 30 min
    1. Redistributing of tasks and doing short standups regarding problems currently facing.
    2. Agreed on a consistent data structure. Drew out diagram of how we would store user and channel information. 
    3. Prepared the first draft of channel.py channels.py and auth.py. 

1st Oct  
Duration: 2.5 hours 
Type of Meeting: Stand up and Pair Programming

    1. Pair programming, where we helped each other to resolve issues with git pull and merge conflicts, which were particularly difficult at first. 
    2. Agreed on a consistent data structure.
    3. Updated data store to include channel messages field. 

Issues Raised:
- Trouble resolving merge conflicts
- Inconsistent data structure fields resulting in key errors across functions.
- Technical issues with using list comprenhension and more pythonic techniques 


2nd Oct  
Duration: 8 hours 
Type of Meeting: Stand up, pair programming and code review

From 12:00 to 17:00:
    1. Implemented tests that drew upon multiple files to the test the holistic functionality of UNSW Streams
    2. Making the TODO list for the next period, including the reassignment of tasks and setting of priorities as new issues emerged. 
 
 Issues Raised:
 - Worked in pairs with screenshare to debug each other's code
 - Inconsistent code styles (variable names convention)
 - General misinterpretation of exceptions (when Input or Access Error should be raised) and specifications across team members
 - Trouble understanding other member's test functions, leading to modification of tests with fewer asserts under each test to allow for easier debugging. 

From 22:00 to 01:00:

    1. Specifically dealing with channel_join, channel_messages and channel_invite which encountered minor issues. 
    2. Added docstrings and comments to all functions. 

3th Oct 

Summarising the iteration 1 from 3pm to 7pm
    1. Coming up with assumptions for all function written
    2. Fixing channel_mesage indexes and return types. 
    3. Checking all pytests passed.
    4. Changing the invalid auth_user_id exceptions to AccessError.
    5. Merging meeting.md and assumption.md into master. 
    6. Finally checking that we satisfied all assignment requirements and marking criteria, such as returning correct types, raising correct errors and correct documentation of code using docstrings.




Iteration 2

12 October: 8 - 8:45pm 

1. We cleared up questions that team members had such as:
- How and where we will store the new functions
- Whether we should make new modules or edit existing ones from iteration 1
- Whether we had to rewrite the pytests using HTTP requests for iteration 1 functions

2. Discussed things we coudld've improved on in Iteration 1
- Make commit messages more descriptive
- Improve meeting logs and be more specific with meeting minutes 
- Keep making sure there's a green tick on master branch
- Merge into master more frequently 

3. Delegated tasks and roles
- Jayden: Writing tests and implementation for auth register and login functions v2.
- Ruosong: Implementation and tests for user functions
- James: tests and implementation for channels/listall/v2, channels/list/v2 and channels/create/v2.
- William: doing functions and tests for channel/invite/v2, channel/join/v2, channel/messages/v2
and channel/leave/v1
- Eric: making tests and implementing channel/details/v2

19 October: 10 - 11pm
1. We talked about our progress for the week as well as our plans and rough estimates on
when we would be able to get our respective parts done.

What we got done included:
Jayden:
- wrote http tests for auth functions
- modified data store to include dms
- wrote functions get_user_from_token and get_token to deal with auth and auth issues 
- wrote tests and implementation for dm create and list
Eric:
- wrote tests for channel_details_v2
Ruosong:
- Almost finished user_test and the structure of user functions
James:
- wrote tests for channels_list_v2 and channels_listall_v2
- almost done with implementation of channels_list_v2 and channels_listall_v2
- need to do tests and implementation for  channels_create_v2
William:
- Almost finished with the tests for the channel functions

2. We also made plans for when we wanted them finished by and also delegated more tasks
Jayden:
- write more tests for dm functions
- implement dm details
Eric:
- write tests for add owner and remove owner
Ruosong:
- Also do the users function
James:
- do the messages functions

21 October: 10:30pm
- We had a quick stand up to get a better understanding of where each person is up to
and whether they needed help. During this time we also did pair programming
where all members would be looking at each others code and check whether we were doing it right
Issues that came up included:
- how to do http tests with confusion on json vs params
- get_json and args.get
- key errors with .json() in tests
Jayden:
- wrote tests and implemented dm_detail, dm_remove and dm_leave
- added exception handling to get user from token
- added fixtures to tests for auth functions
Eric:
- Finished the implementation of channel_details
- Wrote tests for channel add and remove owner
James: 
- Finished the implementation of the channels function
William:
- Finished the implementation of the channel join, invite and leave
Ruosong:
- Finished the user functions

To do list:
- message functions
- store passwords as hashes and modify auth_login accordingly
- implement sessions
- coverage
- admin functions

23 October: 23:30 - 

1. Collect problems we have in our hand right now together with pair-programming and problem solving:
- Ruosong have errors in user_http tests
- William have problems with http tests and the merge conflicts
- Discussed the nature of access and input errors

2. Discussing things we havn't done right now:
- Admin functions havn't completely done 
- coverage test is not satisfactory
- Account for the existence of multiple global owners and their permissions for tests

Jayden: 
- Finish the implementation of the admin functions
Eric:
- Try getting 100% coverage for the channel and user functions
James: 
- Finish the implementation of the message functions
Ruosong:
- Try write more tests for edge cases
William:
- Finish the implementation of the channel functions    





Iteration 3:


05 November 13:15 - 14:30
1. started delegating tasks - added tasks to gitlab issues board and wrote which tasks each person needs to do on discord.
2. discussed documentation - we will do this as a group, and will schedule a meeting once we finish our functions to work on documentation together.
3. discussed possible bonus features we could try - type checking seems the easiest, or a HTML email instead of plain-text.

What we are going to do:
- Everyone will begin implementation of function by tomorrow (06 November - Saturday)
    - Eric - notifications/get
    - James - search, message_share, message_react/unreact, message_pin/unpin
    - Jayden - message_sendlater, message_senddm, auth_password_request/reset
    - William - standup_start, standup_active, standup_send
    - Ruosong - user_profile_uploadpicture, user_stats_v1, users_stats_v1
- Try to get as many functions done as possible by Tuesday (the first auto test)




07 November 21:40 - 22:00
Type of meeting: Asynchronous Meeting

Wrote a calendar to record visually key dates (such as due date and autotests) and goals to finish with due dates

What we did:
Ruosong: 
    - finished with user/profile/upload_photo and half of user and users/stats
    - will push tests and functions once pipeline is passed
Jayden: 
    - finished password_reset_request and password_reset and the associated tests
    - Will finish other two functions by tomorrow night (hopefully)
Eric:
    - Finished writing tests for notifications
James:
    - finished writing tests for message_pin, message_unpin, message_share, message_react and message_unreact
    - working on the implementation for the functions above
William:
    - finish testing for standup_start, standup_active and standup_send.


Issues that were raised:
Eric: 
    - do we raise a notification if someone reacts to their own message?    
    - or if they tag themselves     
William:
    - should we be using the Unix timestamp for all time_stamp related things?
        - Jayden says "yes, so if you hv a datetime object, datetime.now().timestamp() will return an integer"
Ruosong:
    - Some of Ruosong's helper functions may have to work at channel.py channels.py dm.py message.py and standup.py
    - Ruosong's pytest doesn't work for "admin_reset_password"
        - might be because gmail is banned in China




10 November: 14:00 - 14:45
Type of meeting: Standup


What we did:
James:
    - finished implementation for message pin/unpin, share, and react/unreact
Eric:
    - I have checked the frontend is working properly
    - Finished getting 100% coverage for our iteration 2 functions
Jayden:
    - Finished implementing message send later and dm send later function and wrote asssociated tests
    - Implemented notifications for message_send, message edit and invites
    - Wrote tests for and implemented auth/reset_request and password reset
Will:
    - initial implementation of standup functions
    - flask implementation of functions
Ruosong:
    - initial implementation of uploadphoto and user/stats users/stats
    - first version of test for all three


What we are going to do:
James:
    - work on adding more comprehensive tests for the above functions 
Eric:
    - I will be working on fixing up coverage more
    - adding more comprehensive tests
Jayden:     
    - implement notifications for message_react
    - Write more comprehensive and integrated tests for notifications 
    - fix up timestamps for channel messages
Will:
    - test functions (don't think they fully work)
    - write more tests
Ruosong:
    - test for user/stat and users/stats ( those two are literally the same thing)


Issues:
James:
    - incorrect return type for react/pin/unpin
    - incorrect timestamp for channel messages
Eric:
    - Bugs in tests
    - Complications with notification function 
Jayden:
    - Waiting for react message to be merged before implementing react notifications 



11 November 12:30 - 14:00
Type of meeting: Debugging Session/ Pair Programming 

Pair programming between William and Jayden to discuss how to use threading in message_sendlater and standup functions

Issues that were fixed:
William: 
    - not sure what thread function to use (using threading instead of time.sleep())
        - theres a problem with the threading, because when the timer is going the function already returns a value and 
            the save function in the server.py saves the values before the threaded timer finishes
    - merge conflicts
Ruosong:
    - adding a "profile_img_url" field in auth_register return values
    - how dm works and dm_invite



13 November:
Type of meeting: Asynchronous Standup - check-in to see where everyone is at

What we did:
Jayden
    - Added docstrings to notification functions
    - Fixed length of list of notifications to align with specificiations
    - Added more tests for notification functions
Eric
    - Added docstrings to send later functions as well as new messages functions
    - Fixing bugs in tests
James:
    - fixing coverage in message functions
    - fixed bug with initalization of variables
William:
    - working on standup functions to finish them off
Ruosong:
    - Userupload test and funtion upload



14 November: 12:30 - 15:00 and 21:00 - 01:00
Type of meeting: Standup to finalize everything

Meeting with Sean:
    - asked about deployment 404 errors
    - asked about correct formatting/responses for documentation
        - elicitation should not include the solution, let the interviewees just present an issue
        - analysis/specification (use cases), this is where you put the solution
        - technical details for state diagrams ("some of our states were not states")
        - how to use transition effectively in state diagrams
        - acceptance criteria need to tell us about constraints and issues

What we did:
James
    - fixing bugs in messages and message/sendlater
    - deployment of backend 
William
    - Finished fully implementing standup.py and tests 
    - fixed coverage for standup.py
Jayden
    - Conducted documented interviews with sources for elicitation
    - Wrote use cases and user stories for meeting schedule feature
    - Drew state diagram
Eric
    - Added more tests for coverage
    - State diagrams
    - Elicitation, user stories and user cases
Ruosong
    - Implementing part of Elicitation and adding requirements
    - adding few user cases

What we are going to do:
James
    - help out with bug fixing and debugging
    - add to requirements/documentation
William
    - implement type check bonus feature
Jayden
    - Validation and adding constraints to acceptance criteria
Eric
    - Add more information to Design section of documentation 
Ruosong
    - find out problem about the frontened working with upload_photo(tile cannot extend outside the image)
    - adding more features to implementing Interface Design
Issues:
William
    - typecheck list issue
Jayden
    - How to transistion in state diagrams
Eric
    - How to make the state diagrams better as well as the elicitation structure 
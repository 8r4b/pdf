css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; align-items: center;
}
.chat-message.user {
    background-color: #2b313e;
}
.chat-message.bot {
    background-color: #475063;
}
.chat-message .avatar {
    width: 15%;
    font-size: 4rem;        /* BIG emoji */
    text-align: center;
    color: #fff;
    background-color: #3a3f51;  /* circle background */
    border-radius: 50%;
    padding: 0.3rem;
    user-select: none;
    margin-right: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
}
.chat-message .message {
    width: 85%;
    padding: 0 1rem;
    color: #fff;
    font-size: 1.1rem;
    line-height: 1.4;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">🤖</div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">👤</div>
    <div class="message">{{MSG}}</div>
</div>
'''

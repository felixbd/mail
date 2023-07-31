"""
Status code  -->  Plain text message
https://www.ionos.com/digitalguide/e-mail/technical-matters/smtp/
"""

"""
Status codes that indicate that the server has successfully carried out the command:
"""
SUCCESSFUL: dict[int, str] = {200: 'Non-standard success',
                              211: 'System status or system help reply',
                              214: 'Help message',
                              220: 'Server ready for SMTP session',
                              221: 'Server ends the connection',
                              250: 'Requested mail action OK, completed',
                              251: 'User not local; mail is forwarded',
                              252: 'Cannot verify (VRFY) user, but will accept message and attempt delivery',
                              253: 'Pending messages for node started'}

"""
Status codes that indicate that the server has understood the command, but requires further information for processing:
"""
UNDERSTOOD: dict[int, str] = {354: 'Server starts mail input'}

"""
Status codes that indicate that the server has detected a temporary error, but that the command may still be processed:
"""
TEMP_ERROR: dict[int, str] = {421: 'Server not available, connection is terminated',
                              450: 'Commando not executed, mailbox unavailable',
                              451: 'Requested action aborted: local error in processing',
                              452: 'Requested action not taken: insufficient system storage'}

"""
Status codes that indicate that the server has detected a fatal error and the command cannot be processed:
"""
FATAL_ERROR: dict[int, str] = {500: 'Syntax error, command unrecognized',
                               501: 'Syntax error in parameters or arguments',
                               502: 'Command not implemented',
                               503: 'Bad sequence of commands',
                               504: 'Command parameter not implemented',
                               521: 'Server doesn’t accept any mails',
                               530: 'Access denied; authentication required',
                               550: 'Requested action not taken: mailbox unavailable',
                               551: 'User not local; please try forward path',
                               552: 'Requested mail action aborted: exceeded storage allocation',
                               553: 'Requested action not taken: mailbox name not allowed',
                               554: 'Transaction failed'}

"""
All status codes in one dictionary
"""
STATUS_CODES: dict[int, str] = {**SUCCESSFUL, **UNDERSTOOD, **TEMP_ERROR, **FATAL_ERROR}

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 17:25:59 2018

@author: root
"""

"""

Params:

    Here you can insert three logos encoded as base64 string, using python's
    base64 library or using fore example an online tool like:
    https://www.fastix.org/test/Data-URL-Generator.php
        logo_right      string
        logo_left       string
        logo_center     string

    here you can define the layout in html
        header_html     string

"""
#%%
# =============================================================================
# EEG LOGO png to base64
# =============================================================================
logo_right="""
iVBORw0KGgoAAAANSUhEUgAAAIwAAACHCAMAAADz2UHPAAAABGdBTUEAANbY1E9YMgAAABl0RVh0U
29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAABCUExURQ1nmf///0mNsoazzMLZ5UmMshxwn6
TG2O/1+ODs8liWuDqDrGegv3apxbPP39Hi6yt6pZW80jqDqyt5pWefvgAAAHhO7FQAAAAWdFJOU//
//////////////////////////wAB0sDkAAADbklEQVR42uzc6ZarIAwA4BQpIGjV9t73f9WxWCub
Vlygcyb8meWgfmKwmljh/xc1QMxKzBWStYdcxDwgdfs3h7lDhsbCGAZ5WgiTy2JqIOcxcjXjbxkt8
HAwLCcGHExWC9wtjMyLAQvDvgkDiPmEIZfINixm/4+Et0itTgViEIMYxCAGMYjZhdnYEJMbU1gtMy
YUr4hBDGIQgxjEIAYxiEEMYn4dpkmEKee3s0p8KMY+Ak2wj0yF4XavdkUfdhqmsHvxQJfW7lLCaRg
3k6I+HcnL7TwMCGe/vQJW7XCrEzFOQFwaR1O5SSZ2Ika6G2vUQky5R+lgjHOm6Zso3jtPGi/7Jk/F
VH66T/DnJlnhU5y5dDjGH5q+0bmUpTwZIyMwFE7GuCeSBYxoT8cwsRZTwemYwGbDGA4JMP6MCmIoJ
MF4mhCmYYkwriaA4QxSYUCJZUyx71mIOAyw2wKmJJAU05/9yjlMwSA1po+cMoARvJ1f4kRML+DCxt
yqxeeFDq2qhEK56mj3/El5QT51xieLEIMYxCAGMYhBTHKMIoQ4uTJG7OZcbvWNmT3bFRhl3Ge1U1Z
HORke6t+NkcvSRaG5PFmdlBbTip55OGGk5OqdmDH3ux7Dp6XolEq5OTnMbZhX3nE9pnr3ZHoF3Xu8
StiLea1sPaZ9H105ZbyUmz2YwxQfbjJIHEbnw4SRTm3HkKkOwDSRmG4Mj9etWD2GTHsARneIwMiXQ
BkpW+HWSjZjnrsZgWEvQT1FopqCbzemicLoipkwCmdycEmImU0kgCnFMOgxGJ1bV3qAaqFnEfey/Z
swtB5ynTEY3bfW5xvF9eQuvU1vwwyjTWMwOlxvA0OTpB8NGzHDpOAxmOdEFkLHrD5Yjb/2OQwfP7N
ZEGOUV9ZiamP3xry3ANg9mygY02ItRhmAOlwg2owh0XXtckplj3XO+iDMcIKPwXAjx18Gq8PbMayM
xFRGHbELVqvmMHQu4zZdQJJITGsk+VWw+LDpeoZOkzXmWYjGCBMRqsrswQy1oPWYzggT/7NgJwZkH
IZQSnng9ymq+qBwRqstlrK0hblA3f+x6cGMP35H+VXfvf2qbyVnPk5XG/P4hoH5iu/4X11Mxqhh/n
sh7tkPkvnGjHvucbFfbJLDcp99y0rywHl8eBnONVmT+Jqg34n5EWAAWPvv3taQxlYAAAAASUVORK5
CYII=
"""
#%%
# =============================================================================
#
# =============================================================================
logo_left="""
iVBORw0KGgoAAAANSUhEUgAAAKQAAABPCAMAAABS6J4yAAAABGdBTUEAANbY1E9YMgAAABl0RVh0U
29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAEpUExURQwKDAxmNAxmTBRmXCR6LCwqLAxCJK
zKtAxWRDxGRDyWNAxOLHRydHx+fFReVGRmZCRWJOzq7BQ+NExOTCxCNIyGjNze3MTitNTO1MTCxMz
KzLSytKSipKSmpNTW1JSunHyWjFx6XLTOvKTGzJSSlKyurJSWlDRqJLS6tOTi5MS+vKSenIyOjJya
nDx6NNzi5NTm1OTm5NTW3Ly6vLy2tNza1OTm7JSalOTy3KyqrLS6vJyWnJSOlLzWxMze5KzOzLTGx
JSOjMzKxKy6pOzm5MTazOTi3Ly+xNzu7LSurOTq5Jy6xNzW1MzGzOz25KSulJSanMTS3KSmrNTm9N
zW3NTe1JyepMzW3LzCxMTOxLzCrKzO1NzKzKSqtOTq7NTi5MTGzMzaxAAAALtzERYAAABjdFJOU//
/////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////AHc1DpsAAAhgSURBVHja5JsJd
+I4EscViIwdWzbGNjHhPgIkJKRz351zkj63zzl2rt3V9/8QW1USBDL9NvtYPPG8VZp+xqbDzyXVv/
4qaCYTHMU5/R6WION3Mv2QP/4FIA9aMvWQL3Pt9EPmcjL1kMW3X1IP+SXXkqmHbOVeph7y1RyzJjH
IT7kX6YRc8yX9+FLW6j/56YQMC3oY3DCMAjzCfN5LF+Sunc3AWBiPxcXFpcWNdEEKQjQzC5kHyqV8
nC7IwMxkphEB0krXmiwWABBCaY9GPt9b7DnpghzYNNum95toNsThYeXwh8PNw510QXoqa4xr2WrPV
yRngvzHtwUIFiRMeOFNLjdP/zMr5JdP3zj5Hmcb8sbbumy1/v78kPLH9h83WJEJhAsZM3RxeI7nOF
H0rBWn+PaXV49OuZmMlvL8WILC5y2LL9vt7x8LEEmkOVlvSH+2buJq1O3Tq2qDqHOPBycr/vVqTcr
SYdTdOynJorpeLBfnmd1+u93ennh+ZVLaPGg5VpsVynrGAnhEdBg4AXOl/CdjnPPKrYUnOJw5ZiV0
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
h83yEt2AAAAABJRU5ErkJggg==
"""
#%%
# =============================================================================
#
# =============================================================================
logo_center= """
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
"""

#%%
# =============================================================================
#
# =============================================================================
header_html ="""
<div>
<table style="width: 100%;">
<tbody>
<tr>
<td><a href=""><img height="79" width="153" style="float: left;"
alt="logo-l" src='data:image/png;base64,"""+logo_left+"""'></a></td>
<td style="text-align: center;"><img height="54" width="482" style="margin-top: 10px;
margin-right: 5px; margin-bottom: 5px; margin-left: 5px;"
alt="logo-c" src='data:image/png;base64,"""+logo_center+"""'><br><span style="font-size: 8pt;"></span></td>
<td><a href="" target=""><img height="78" style="float: right;"
alt="logo-r" src='data:image/png;base64,"""+logo_right+"""'></a></td>
</tr>
</tbody>
</table>
</div>
"""
#%%
# =============================================================================
# 
# =============================================================================
font_style="""
<style>
h1 { color: #111; font-family: 'Open Sans Condensed', sans-serif; font-size: 64px; font-weight: 700; line-height: 64px; margin: 0 0 0; padding: 20px 30px; text-align: center; text-transform: uppercase; }
p { color: #f2f2f2; background: #ff4a4a; font-size: 15px; line-height: 15px; font-weight: 700; margin: 0 1px 12px; float: left; padding: 12px; margin: 0 1px 12px; font-family: 'Libre Baskerville', serif; }
</style>
"""


# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 13:43:57 2018

@author: root
"""
# =============================================================================
# 
# =============================================================================
"""
Params:

    Here you can insert three logos encoded as base64 string, using python's
    base64 library or using for example an online tool like:
    https://www.fastix.org/test/Data-URL-Generator.php
        logo_right      string
        logo_left       string
        logo_center     string

    here you can define the layout in html
        header_html     string

"""
# =============================================================================
# 
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
# =============================================================================
# 
# =============================================================================
logo_center = """PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4NCjwhLS0gR2VuZXJhdG9yOiBBZ
G9iZSBJbGx1c3RyYXRvciAxNy4wLjAsIFNWRyBFeHBvcnQgUGx1Zy1JbiAuIFNWRyBWZXJzaW9uOi
A2LjAwIEJ1aWxkIDApICAtLT4NCjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkc
gMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0
ZCI+DQo8c3ZnIHZlcnNpb249IjEuMSIgaWQ9IkNhbHF1ZV8xIiB4bWxucz0iaHR0cDovL3d3dy53M
y5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIi
B4PSIwcHgiIHk9IjBweCINCgkgd2lkdGg9IjMzNS44NTdweCIgaGVpZ2h0PSIxODYuOTY2cHgiIHZ
pZXdCb3g9IjAgMCAzMzUuODU3IDE4Ni45NjYiIGVuYWJsZS1iYWNrZ3JvdW5kPSJuZXcgMCAwIDMz
NS44NTcgMTg2Ljk2NiINCgkgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+DQo8Zz4NCgk8bGluZSBmaWxsP
SJub25lIiBzdHJva2U9IiMwQUE3QjgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLW1pdGVybGltaX
Q9IjEwIiB4MT0iMCIgeTE9IjE4NS45NjYiIHgyPSIzMzUuODU3IiB5Mj0iMTg1Ljk2NiIvPg0KCTx
nPg0KCQk8cGF0aCBmaWxsPSIjMEFBN0I4IiBkPSJNNTQuMjg3LDE2OC42MDdjLTEuMzE2LDAtMi42
MzMtMC42OTMtMi42MzMtMi41NjR2LTE5Ljg4NWwtMTYuNDIsMHYxOS44ODUNCgkJCWMwLDEuNzMyL
TEuMzE3LDIuNTY0LTIuNjMzLDIuNTY0Yy0xLjMxNiwwLTIuNjMzLTAuODMyLTIuNjMzLTIuNTY0Vj
EyMi42YzAtMS43MzIsMS4zMTctMi42MzMsMi42MzMtMi42MzMNCgkJCWMxLjMxNiwwLDIuNjMzLDA
uOTAxLDIuNjMzLDIuNjMzdjE4LjI5MmwxNi40MiwwVjEyMi42YzAtMS43MzIsMS4zMTctMi42MzMs
Mi42MzMtMi42MzNjMS4zMTcsMCwyLjYzMywwLjkwMSwyLjYzMywyLjYzM3Y0My40NDMNCgkJCUM1N
i45MiwxNjcuOTE0LDU1LjYwNCwxNjguNjA3LDU0LjI4NywxNjguNjA3eiIvPg0KCQk8cGF0aCBmaW
xsPSIjMEFBN0I4IiBkPSJNMTIzLjMyNiwxMjUuMTIybC03LjYyMSwwdjQwLjM5NGMwLDEuNzMyLTE
uMzE3LDIuNTY0LTIuNjMzLDIuNTY0Yy0xLjMxNywwLTIuNjMzLTAuODMyLTIuNjMzLTIuNTY0DQoJ
CQl2LTQwLjM5NGwtNy42MjEsMGMtMS43MzMsMC0yLjYzMy0xLjMxNi0yLjYzMy0yLjYzM2MwLTEuM
zE2LDAuOS0yLjYzMywyLjYzMy0yLjYzM2wyMC41MDksMGMxLjczMiwwLDIuNjMzLDEuMzE2LDIuNj
MzLDIuNjMzDQoJCQlTMTI1LjA1OCwxMjUuMTIyLDEyMy4zMjYsMTI1LjEyMnoiLz4NCgkJPHBhdGg
gZmlsbD0iIzBBQTdCOCIgZD0iTTE3Mi41MTgsMTY4LjA4Yy0xLjMxNywwLTIuNjMzLTAuODMyLTIu
NjMzLTIuNTY0di0zMy44ODFsLTkuMTQ2LDIwLjk5NA0KCQkJYy0wLjU1NCwxLjMxNi0xLjczMiwxL
jgwMS0yLjkxLDEuODAxYy0xLjMxNiwwLTIuNDI1LTAuNjI0LTIuOTc5LTEuODAxbC05LjQyMy0yMC
45OTR2MzMuODgxYzAsMS43MzItMS4zMTcsMi41NjQtMi42MzMsMi41NjQNCgkJCWMtMS4zMTYsMC0
yLjYzMy0wLjgzMi0yLjYzMy0yLjU2NHYtNDMuMDI3YzAtMS44NzEsMC42OTMtMy4wNDksMy4xMTgt
My4wNDloMC4yMDhjMS44NywwLDIuNjMzLDAuOTcsMy4xMTcsMi4wMDlsMTEuMDg2LDI0LjgwNQ0KC
QkJbDExLjAxNi0yNC44MDVjMC40ODUtMS4wMzksMS4yNDctMi4wMDksMy4xODgtMi4wMDloMC4yMD
hjMi40MjUsMCwzLjA0OCwxLjE3OCwzLjA0OCwzLjA0OXY0My4wMjcNCgkJCUMxNzUuMTUsMTY3LjI
0OCwxNzMuODM0LDE2OC4wOCwxNzIuNTE4LDE2OC4wOHoiLz4NCgkJPHBhdGggZmlsbD0iIzBBQTdC
OCIgZD0iTTIyMS4yOTIsMTY4LjA4Yy0xLjAzOCwwLTIuMDc4LTAuNDg1LTIuNDk0LTEuODAybC0zL
jA0OS05Ljk3N2wtMTcuMTE0LDBsLTMuMTE4LDkuOTc3DQoJCQljLTAuNDE2LDEuMzE2LTEuMzg2LD
EuODAyLTIuNDI1LDEuODAyYy0xLjU5NCwwLTIuNzAyLTEuMTA5LTIuNzAyLTIuNDk1YzAtMC4yMDg
sMC4wNjktMC40ODUsMC4xMzgtMC44MzFsMTMuNTExLTQzLjM3NA0KCQkJYzAuNDE2LTEuMzE2LDEu
NzMyLTEuOTQsMy4xMTgtMS45NGMxLjQ1NCwwLDIuNzcxLDAuNjI0LDMuMTg3LDEuOTRsMTMuNTExL
DQzLjM3NGMwLjA2OSwwLjM0NiwwLjEzOCwwLjYyMywwLjEzOCwwLjgzMQ0KCQkJQzIyMy45OTUsMT
Y2Ljk3MSwyMjIuODg2LDE2OC4wOCwyMjEuMjkyLDE2OC4wOHogTTIwNy4xNTksMTI4Ljg2NGwtNi4
4NTksMjIuMTcybDEzLjc4NywwTDIwNy4xNTksMTI4Ljg2NHoiLz4NCgkJPHBhdGggZmlsbD0iIzBB
QTdCOCIgZD0iTTI1My4wMjUsMTQ2LjA0NmwtOC41MjMsMHYxOS40N2MwLDEuNzMyLTEuMzE3LDIuN
TY0LTIuNjMzLDIuNTY0Yy0xLjMxNiwwLTIuNjMzLTAuODMyLTIuNjMzLTIuNTY0DQoJCQl2LTQzLj
AyN2MwLTEuMzg2LDEuMjQ3LTIuNjMzLDIuNjMzLTIuNjMzbDExLjE1NiwwYzcuMjc1LDAsMTMuMTY
0LDUuNzUxLDEzLjE2NCwxMy4wMjYNCgkJCUMyNjYuMTg5LDE0MC4xNTcsMjYwLjMsMTQ2LjA0Niwy
NTMuMDI1LDE0Ni4wNDZ6IE0yNTMuMDI1LDEyNS4xMjJsLTguNTIzLDB2MTUuNjU4bDguNTIzLDBjN
C4zNjUsMCw3Ljg5OC0zLjUzNCw3Ljg5OC03Ljg5OA0KCQkJQzI2MC45MjMsMTI4LjY1NiwyNTcuMz
ksMTI1LjEyMiwyNTMuMDI1LDEyNS4xMjJ6Ii8+DQoJCTxwYXRoIGZpbGw9IiMwQUE3QjgiIGQ9Ik0
yOTIuNjU1LDE2OC4wOGwtMC42MjQsMGMtNy4xMzcsMC0xMy43MTktNC4zNjUtMTMuNzE5LTEyLjc0
OWMwLTEuNzMyLDEuMzE2LTIuNTY0LDIuNjMzLTIuNTY0DQoJCQljMS4zMTYsMCwyLjYzMywwLjc2M
iwyLjYzMywyLjYzM2MwLDQuOTIsNC4wMTksNy40ODMsOC41MjIsNy40ODNoMC42OTNjNS40NzQsMC
w3LjgyOS0yLjcwMiw3LjgyOS03LjY5MQ0KCQkJYzAtNS42ODEtNC4wMTktNy4yNzUtOC4yNDUtOS4
2MzFjLTYuNjUyLTMuNzQyLTEzLjM3My01LjQwNC0xMy4zNzMtMTQuMjczYzAtNi43MjEsNS43NTEt
MTEuODQ4LDEzLjAyNy0xMS44NDhsMC42OTIsMA0KCQkJYzYuNjUyLDAsMTIuNjExLDQuNzExLDEyL
jYxMSwxMS4wODZjMCwxLjczMi0xLjE3OCwyLjU2NC0yLjQ5NSwyLjU2NGMtMS4zMTYsMC0yLjU2My
0wLjgzMi0yLjc3MS0yLjQ5NQ0KCQkJYy0wLjM0Ni0zLjM5NS0zLjI1Ny01Ljg4OS03LjQ4My01Ljg
4OWwtMC42MjQsMGMtNS43NSwwLTcuNjIxLDQuMTU3LTcuNjIxLDYuNTgyYzAsNS4wNTgsNC4yOTYs
Ni41ODIsOC4wMzcsOC41OTENCgkJCWM2LjkyOSwzLjc0MiwxMy41MTEsNS45NTksMTMuNTExLDE1L
jM4MkMzMDUuODg4LDE2My4yMywzMDEuMDM4LDE2OC4wOCwyOTIuNjU1LDE2OC4wOHoiLz4NCgkJPG
c+DQoJCQk8cGF0aCBmaWxsPSIjMEFBN0I4IiBkPSJNNzguNzc2LDE0My4xNzFjLTYuMDI1LDAtMTI
uMTI1LTQuMjc2LTEyLjEyNS0xMi40NDZjMC04LjIwOCw2LjEwNy0xMi41MDMsMTIuMTQtMTIuNTAz
DQoJCQkJYzYuMDQ2LDAsMTIuMTY3LDQuMjk0LDEyLjE2NywxMi41MDNDOTAuOTU3LDEzOC44OTUsO
DQuODI5LDE0My4xNzEsNzguNzc2LDE0My4xNzF6IE03OC43OSwxMjMuMDQ0DQoJCQkJYy0zLjY0Mi
wwLTcuMzE2LDIuMzc1LTcuMzE2LDcuNjhjMCw1LjI2NiwzLjY2Nyw3LjYyMyw3LjMwMiw3LjYyM2M
zLjY2MiwwLDcuMzU4LTIuMzU3LDcuMzU4LTcuNjIzDQoJCQkJQzg2LjEzNCwxMjUuNDIsODIuNDQ1
LDEyMy4wNDQsNzguNzksMTIzLjA0NHoiLz4NCgkJPC9nPg0KCQk8cGF0aCBmaWxsPSIjRTI0NDQ5I
iBkPSJNMTkxLjA4Miw2MS45NzFjMC42MDQtMS4xOTksMS42NjgtMi4zMzMsMi4wMTUtMy42NTVjMy
44NjgtMTQuNzM5LTEwLjQyMS0zMS4yNi0zMS45MTYtMzYuOQ0KCQkJYy0xNy42NjUtNC42MzUtMzQ
uMzU3LTAuNTI5LTQyLjAxMiw5LjI4MUMxMjEuMTk4LDMxLjcxMSwxODguNDQyLDYxLjg5NiwxOTEu
MDgyLDYxLjk3MXoiLz4NCgkJPGc+DQoJCQk8ZGVmcz4NCgkJCQk8cGF0aCBpZD0iU1ZHSURfMV8iI
GQ9Ik0xNjEuMzk4LDIwLjk4MWMtMTcuNjY1LTQuNjM1LTM0LjU4OC0wLjQxLTQyLjI0NCw5LjRjMC
4wMzEsMC4wMTYtMC4wMzEtMC4wMTYsMCwwDQoJCQkJCWMtMC4wMTcsMC4wMDUtMC4wMzcsMC4wMS0
wLjA1NCwwLjAxNWMtMC40ODcsMi41NDQtMC43NTksNS4xOC0wLjc1OSw3LjkwMWMwLDEwLjQ0Miwz
Ljc2MSwxOS41OTUsOS45NDIsMjYuNTM5bDAuNjg0LDAuNzM3DQoJCQkJCWMwLjYzMSwwLjY1OCwxL
jI2MywxLjMxNSwxLjkyLDEuOTJsMjcuNjk2LDI3LjY5NmwzMC4zMjYtMzAuMzUzYzAsMCwxLjQ1NC
0xLjc3NiwyLjMyMy0zLjAxMQ0KCQkJCQljMC4xMzEtMC4yMDItMC4yNTItMC4yMTctMC4wMjktMC4
yMWMwLjYwNC0xLjE5OSwxLjc2Mi0yLjQxMiwyLjEwOS0zLjczNEMxOTcuMTgyLDQzLjE0MiwxODIu
ODkyLDI2LjYyMiwxNjEuMzk4LDIwLjk4MXoiLz4NCgkJCTwvZGVmcz4NCgkJCTxjbGlwUGF0aCBpZ
D0iU1ZHSURfMl8iPg0KCQkJCTx1c2UgeGxpbms6aHJlZj0iI1NWR0lEXzFfIiAgb3ZlcmZsb3c9In
Zpc2libGUiLz4NCgkJCTwvY2xpcFBhdGg+DQoJCQk8ZyBjbGlwLXBhdGg9InVybCgjU1ZHSURfMl8
pIj4NCgkJCQkNCgkJCQkJPGltYWdlIG92ZXJmbG93PSJ2aXNpYmxlIiBvcGFjaXR5PSIwLjciIHdp
ZHRoPSIzODQiIGhlaWdodD0iMzUyIiB4bGluazpocmVmPSI1ODY1MTM2MTYzMjA4NDQwLnBuZyIgI
HRyYW5zZm9ybT0ibWF0cml4KDAuMjQgMCAwIDAuMjQgMTEyLjMxNjMgMjIuODQ2MykiPg0KCQkJCT
wvaW1hZ2U+DQoJCQkJPGc+DQoJCQkJCTxwYXRoIGZpbGw9IiMwQUE3QjgiIGQ9Ik0xNTYuNzU2LDM
4Ljk1NWMtMTUuMzctMTEuNjczLTI5LjAxLTExLjE0Mi0zNy42NTYtOC41NTljLTAuNDg3LDIuNTQ0
LTAuNzU5LDUuMTgtMC43NTksNy45MDENCgkJCQkJCWMwLDEwLjQ0MiwzLjc2MSwxOS41OTUsOS45N
DIsMjYuNTM5bDAsMGwwLjY4NCwwLjczN2MwLjYzMSwwLjY1OCwxLjI2MiwxLjMxNSwxLjkyLDEuOT
JsMjcuNjk2LDI3LjY5NmwzMC4zMjYtMzAuMzUzbDAsMA0KCQkJCQkJYzEuNTE1LTEuNzAzLDIuMzg
yLTIuOTI4LDMuMzI5LTQuNjM2QzE3OS4xMjcsNTguNTEsMTc1LjgsNTMuNDE5LDE1Ni43NTYsMzgu
OTU1eiIvPg0KCQkJCTwvZz4NCgkJCTwvZz4NCgkJPC9nPg0KCQk8cGF0aCBmaWxsPSIjMEFBN0I4I
iBkPSJNMTk3Ljc4Niw0MC4zN2MwLjE0OC0xMC44Ny0zLjg4MS0yMS4wMTQtMTEuMzQ1LTI4LjU2Nm
MtNy4zNzUtNy40NjQtMTcuMzMxLTExLjY1NC0yOC4wMzEtMTEuOA0KCQkJYy0xOC45NTUtMC4yNDE
tMzUuMTExLDEyLjM4Mi0zOS4zNDQsMzAuNTc0bDUuOTA2LDEuMjUxYzMuNTg1LTE1LjQwNywxNy4z
MzQtMjYuMDA3LDMzLjM1NS0yNS43OTYNCgkJCWM5LjEwOSwwLjEyNCwxNy41NywzLjY3OSwyMy44M
jYsMTAuMDA5YzYuMzE5LDYuMzk0LDkuNzMsMTUuMDA1LDkuNjA0LDI0LjI0NmMtMC4wODksNi41Mz
QtMi4yNiwxMy4zOTMtNS45NTUsMTguODE5bDMsNS43OTQNCgkJCWMwLDAsMS41NTctMS43ODMsMi4
4NDUtMy42NjdjMC4xMDMtMC4xNSwwLjE0Mi0wLjIxOSwwLjI2Ny0wLjQzN0MxOTUuNjUzLDU0LjY2
NSwxOTcuNjg4LDQ3LjUxMywxOTcuNzg2LDQwLjM3eiIvPg0KCTwvZz4NCjwvZz4NCjwvc3ZnPg0K"""

#%%
# =============================================================================
#
# =============================================================================
header_html ="""
<div>
<table style="width: 100%;">
<tbody>
<tr>
<td><img height="79" width="153" style="float: left;"
alt="logo-l" src='data:image/png;base64,"""+logo_left+"""'></td>
<td style="text-align: center;"><img height="79" width="456" style="margin-top: 10px;
margin-right: 5px; margin-bottom: 5px; margin-left: 5px;"
alt="logo-c" src='data:image/svg+xml;base64,"""+logo_center+"""'><br><span style="font-size: 8pt;"></span></td>
<td><img height="78" style="float: right;"
alt="logo-r" src='data:image/png;base64,"""+logo_right+"""'></td>
</tr>
</tbody>
</table>
</div>
"""
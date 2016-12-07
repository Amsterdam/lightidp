from datetime import datetime
import time

from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User

TEST_USER = 'testuser'
PASSWORD = 'just_a_password'


class AuthenticationServiceTest(APITestCase):
    def test_header_in_code(self):
        response = self.client.get('/authenticatie/echo', {}, **{'HTTP_X_SAML_ATTRIBUTE_TOKEN1':
            'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c2FtbDpBc3NlcnRpb24geG1sbnM6c2FtbD0idXJuOm9hc2lzOm5hbW'
            'VzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiIgSUQ9IklEMTFGQkFEQjk0OTJBNUI4MTVEQjE5MTcwRjNEMTYxMkI0MjlBMzQ5IiBJc3N1ZUlu'
            'c3RhbnQ9IjIwMTYtMTItMDdUMTE6MzY6MTMuOTkzWiIgVmVyc2lvbj0iMi4wIj48c2FtbDpJc3N1ZXIgRm9ybWF0PSJ1cm46b2FzaXM6bm'
            'FtZXM6dGM6U0FNTDoyLjA6bmFtZWlkLWZvcm1hdDplbnRpdHkiIHhtbG5zOnNhbWw9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDph'
            'c3NlcnRpb24iPmh0dHBzOi8vdG1hLmFjYy5hbXN0ZXJkYW0ubmwvYXNlbGVjdHNlcnZlci9zZXJ2ZXI8L3NhbWw6SXNzdWVyPjxkczpTaW'
            'duYXR1cmUgeG1sbnM6ZHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyMiPgo8ZHM6U2lnbmVkSW5mbyB4bWxuczpkcz0i'
            'aHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+CjxkczpDYW5vbmljYWxpemF0aW9uTWV0aG9kIEFsZ29yaXRobT0iaHR0cD'
            'ovL3d3dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIiB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2ln'
            'IyIvPgo8ZHM6U2lnbmF0dXJlTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI3JzYS1zaGExIi'
            'B4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyIvPgo8ZHM6UmVmZXJlbmNlIFVSST0iI0lEMTFGQkFEQjk0'
            'OTJBNUI4MTVEQjE5MTcwRjNEMTYxMkI0MjlBMzQ5IiB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+Cj'
            'xkczpUcmFuc2Zvcm1zIHhtbG5zOmRzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjIj4KPGRzOlRyYW5zZm9ybSBBbGdv'
            'cml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNlbnZlbG9wZWQtc2lnbmF0dXJlIiB4bWxuczpkcz0iaHR0cDovL3'
            'd3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyIvPgo8ZHM6VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8x'
            'MC94bWwtZXhjLWMxNG4jIiB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+PGVjOkluY2x1c2l2ZU5hbW'
            'VzcGFjZXMgeG1sbnM6ZWM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyIgUHJlZml4TGlzdD0iZHMgc2FtbCB4'
            'cyB4c2kiLz48L2RzOlRyYW5zZm9ybT4KPC9kczpUcmFuc2Zvcm1zPgo8ZHM6RGlnZXN0TWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy'
            '53My5vcmcvMjAwMC8wOS94bWxkc2lnI3NoYTEiIHhtbG5zOmRzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjIi8+Cjxk'
            'czpEaWdlc3RWYWx1ZSB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+czRpV2JJN0YxbWxBVklLTW9QcD'
            'ZZRE8ySUtrPTwvZHM6RGlnZXN0VmFsdWU+CjwvZHM6UmVmZXJlbmNlPgo8L2RzOlNpZ25lZEluZm8+CjxkczpTaWduYXR1cmVWYWx1ZSB4'
            'bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+CldSVFl6eDAvZzdYMzNHVzZOSE1aWTNTazlGZm9wMkpSbn'
            'FaRXNaa1ByTGMrNCtyOU1LTUV3b3JnaytlajJrWW1GbDUvRjlIbTVFeTAKQ2gyT2EzalVVOVhuRW96MS9kR0VFdEJsSnY3Z3cwUmVLUkhM'
            'WDUyZFFZck5CakVuYksvcFV3d3R6bDVwUDdva2o1dVZlMU9SUHhsMgp0Sm9lTldNdWhmL1JuSGhhVWFjcUNZZXFaek9jKzVtOFlReTMwdW'
            'Z4d1lqTGtvT0IvWU9Udzl4Um0yWFBiMG4rL2pDaFlmVkRhMU83CmRXTDlRMlZWbjRZT213MVBweXdHeVcydXNPaDVXWWtBLzFxcDJaQ1FU'
            'LzZPam9JbHlnOUpBZkQwMXFkZmpUYVRMeVRqNmhVNmxscGkKY2dYeTFQc2NOYUJHVlFOSkw2Q2ZhZFNtNk1Gck9kVEMva0hBNFE9PQo8L2'
            'RzOlNpZ25hdHVyZVZhbHVlPgo8L2RzOlNpZ25hdHVyZT48c2FtbDpTdWJqZWN0IHhtbG5zOnNhbWw9InVybjpvYXNpczpuYW1lczp0YzpT'
            'QU1MOjIuMDphc3NlcnRpb24iPjxzYW1sOk5hbWVJRCBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpuYW1laWQtZm9ybW'
            'F0OnRyYW5zaWVudCIgTmFtZVF1YWxpZmllcj0iaHR0cHM6Ly90bWEuYWNjLmFtc3RlcmRhbS5ubC9hc2VsZWN0c2VydmVyL3NlcnZlciIg'
            'eG1sbnM6c2FtbD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiI+MEJDQTE0NzU1MDU2MDZCM0ZBOTYzNjAwQ0QwMz'
            'M3QjExNDc3OTlDQjA4OTU1MjlERTA1QjkxRDNDM0ZCOTcwQzAyOTg5RkI5RjIzOUEyODY5MEM3OEY0NEFCNkMxQUUxNTFFNkRBMTUzQzFC'
            'NzdEQjVCREY3NUI0QTZFOTNBNUM0NjZCMjBGREFDMjJGNzcyNEU3RTE5ODAzQkFCNkY2NzM2OUMzQjhBMTIxNEMxRTUxQjg4MTkyOTU3N0'
            'M0OUZCRTU2QjBDNUZCNUJDMEExOUExNDA2QzgzRTI5RUFDRjYwNUFDRDQwODA4N0UzQjYwPC9zYW1sOk5hbWVJRD48L3NhbWw6U3ViamVj'
            'dD48c2FtbDpBdHRyaWJ1dGVTdGF0ZW1lbnQgeG1sbnM6c2FtbD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiI+PH'
            'NhbWw6QXR0cmlidXRlIE5hbWU9InVpZCIgeG1sbnM6c2FtbD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiI+PHNh'
            'bWw6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hIiB4bWxuczp4c2k9Imh0dHA6Ly'
            '93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj45MDAxMTU2MzQ8L3NhbWw6QXR0cmli'
            'dXRlVmFsdWU+PC9zYW1sOkF0dHJpYnV0ZT48L3NhbWw6QXR0cmlidXRlU3RhdGVtZW50Pjwvc2FtbDpBc3NlcnRpb24+'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('saml_b64', response.data)
        self.assertIn('PD94bWwgd', response.data['saml_b64'])
        self.assertIn('saml_xml', response.data)
        self.assertIn('900115634', response.data['saml_xml'])

# -*- codingL utf-8 -*-

"""
Errors
~~~~~~~

Copyright (c) 2021 ItsArtemiz (Augadh Verma)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: ItsArtemiz#8858 or https://discord.gg/2NVgaEwd2J

"""

class ChannelNotFound(Exception):
    pass

class InvalidArtist(Exception):
    pass

class NotBotChannel(Exception):
    pass

class NotStaff(Exception):
    pass

class NoDatabaseGiven(Exception):
    pass

class NoCollectionGiven(Exception):
    pass
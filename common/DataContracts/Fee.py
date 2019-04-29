"""
    Copyright 2019 Akvelon Inc.
    Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""

from common.constants.constants import TRANSACTION_INPUT_SIZE_BYTES, TRANSACTION_OUTPUT_SIZE_BYTES, TRANSACTION_METADATA_SIZE_BYTES

class fee:
    """Fee per byte in satoshi.

    * satoshi_per_byte:int -- what fee should be payed per single byte in satoshi.
    """
    def __init__(self, satoshi_per_byte: int):
        self.satoshi_per_byte = satoshi_per_byte

    def get_for_input(self):
        "Returns fee to cover single input"
        return TRANSACTION_INPUT_SIZE_BYTES * self.satoshi_per_byte

    def get_for_output(self):
        "Returns fee to cover single output"
        return TRANSACTION_OUTPUT_SIZE_BYTES * self.satoshi_per_byte

    def get_for_metadata(self):
        "Returns fee to cover single transaction metadata"
        return TRANSACTION_METADATA_SIZE_BYTES * self.satoshi_per_byte

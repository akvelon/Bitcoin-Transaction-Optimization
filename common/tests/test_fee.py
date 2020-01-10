"""
    Copyright 2019 Akvelon Inc.
    Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""

import pytest
from common.datacontracts.fee import Fee
from common.constants.constants import TRANSACTION_INPUT_SIZE_BYTES, TRANSACTION_OUTPUT_SIZE_BYTES, TRANSACTION_METADATA_SIZE_BYTES

class TestFee:
    @pytest.fixture
    def fee(self):
        self.fee_value = 10
        return Fee(self.fee_value)

    def test_get_for_input(self, fee):
        assert fee.get_for_input() == self.fee_value * TRANSACTION_INPUT_SIZE_BYTES

    def test_get_for_output(self, fee):
        assert fee.get_for_output() == self.fee_value * TRANSACTION_OUTPUT_SIZE_BYTES

    def test_get_for_metadata(self, fee):
        assert fee.get_for_metadata() == self.fee_value * TRANSACTION_METADATA_SIZE_BYTES

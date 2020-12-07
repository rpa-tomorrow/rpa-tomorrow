import lib.utils.ner as ner


class TestCrossCheck:
    def test_full_name_returned(self):
        """
        Test that the tags and corresponding full name
        returns the full name when cross checking.
        """
        tags = ["mark", "anderson"]
        persons = ["mark anderson"]
        cc = ner.cross_check_names(tags, persons)

        assert persons == cc

    def test_same_input_same_output(self):
        """
        Test that if tags and persons are the same, cross
        checking should also return the same output.
        """
        tags = ["mark", "evert", "reggie"]
        cc = ner.cross_check_names(tags, tags)

        assert cc == tags

    def test_missing_tag(self):
        """
        Test that when names are missing in persons that are found in
        tags, the cross check should append the missing tags to persons.
        """
        tags = ["mark", "anderson", "evert"]
        persons = ["mark anderson"]
        expected = ["mark anderson", "evert"]
        cc = ner.cross_check_names(tags, persons)

        assert cc == expected

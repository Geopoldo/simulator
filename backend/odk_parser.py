
import pandas as pd
import json

class ODKParser:
    def __init__(self, file_path=None, file_content=None):
        if file_path:
            self.xls = pd.ExcelFile(file_path)
        elif file_content:
            self.xls = pd.ExcelFile(file_content)
        else:
            raise ValueError("Either file_path or file_content must be provided")

    def parse(self):
        survey = self._parse_survey()
        choices = self._parse_choices()
        settings = self._parse_settings()
        
        return {
            "survey": survey,
            "choices": choices,
            "settings": settings
        }

    def _parse_survey(self):
        if 'survey' not in self.xls.sheet_names:
            return []
        
        df = pd.read_excel(self.xls, 'survey')
        # Drop rows with empty 'type' or commented out
        df = df[df['type'].notna()]
        
        # Index choices for easy lookup
        choice_map = self._parse_choices()
        
        questions = []
        group_stack = []

        for _, row in df.iterrows():
            q = row.dropna().to_dict()
            q_type = q.get('type', '')
            
            # Handle Groups
            if q_type == 'begin_group':
                group_name = q.get('name', 'unnamed_group')
                group_label = q.get('label::English (en)') or q.get('label') or group_name
                group_stack.append({'name': group_name, 'label': group_label})
                # Add group itself as an item if we want to show it, or just use it for nesting
                # Let's add it to visualize the structure explicitly
                q['hierarchy'] = [g['label'] for g in group_stack[:-1]] # Parent path
                q['is_group_start'] = True
                questions.append(q)
                continue
            
            if q_type == 'end_group':
                if group_stack:
                    group_stack.pop()
                continue

            # Regular Question
            q['hierarchy'] = [g['label'] for g in group_stack]
            
            # Embed specific choices if type is select
            if q_type.startswith('select_one') or q_type.startswith('select_multiple'):
                parts = q_type.split()
                if len(parts) > 1:
                    list_name = parts[1]
                    q['options'] = choice_map.get(list_name, [])
            
            questions.append(q)
        return questions

    def _parse_choices(self):
        if 'choices' not in self.xls.sheet_names:
            return {}
        
        df = pd.read_excel(self.xls, 'choices')
        choices = {}
        
        # Group by list_name
        for list_name, group in df.groupby('list_name'):
            options = []
            for _, row in group.iterrows():
                opt = row.dropna().to_dict()
                # Remove internal grouping key
                if 'list_name' in opt:
                    del opt['list_name']
                options.append(opt)
            choices[list_name] = options
            
        return choices

    def _parse_settings(self):
        if 'settings' not in self.xls.sheet_names:
            return {}
        df = pd.read_excel(self.xls, 'settings')
        if not df.empty:
            return df.iloc[0].dropna().to_dict()
        return {}

if __name__ == "__main__":
    # Test with local file
    odk = ODKParser(file_path="../ODK/HFA + CARI (FES) + HHS + climate shocks and SEI checked.xlsx")
    parsed = odk.parse()
    print(json.dumps(parsed['settings'], indent=2))
    print(f"Parsed {len(parsed['survey'])} questions")

import argparse
import json
import os
import sys
from datetime import datetime

def human_readable_size(size):
    """Convert bytes to a human-readable format."""
    if size < 1024:
        return f"{size}B"
    size /= 1024
    if size < 1024:
        return f"{size:.1f}K"
    size /= 1024
    if size < 1024:
        return f"{size:.1f}M"
    size /= 1024
    return f"{size:.1f}G"

def print_ls(contents, show_all=False, long_format=False, reverse=False, sort_by_time=False, filter_type=None, human_readable=False):
    """Prints the directory listing in a format similar to the `ls` command."""
    items = [item for item in contents if show_all or not item['name'].startswith('.')]
    if filter_type:
        if filter_type == 'dir':
            items = [item for item in items if 'contents' in item]
        elif filter_type == 'file':
            items = [item for item in items if 'contents' not in item]
        else:
            print(f"error: '{filter_type}' is not a valid filter criteria. Available filters are 'dir' and 'file'")
            sys.exit(1)
    if sort_by_time:
        items.sort(key=lambda x: x['time_modified'], reverse=True)
    if reverse and not sort_by_time:
        items.reverse()
    for item in items:
        if long_format:
            time_formatted = datetime.fromtimestamp(item['time_modified']).strftime('%b %d %H:%M')
            file_type = 'd' if 'contents' in item else '-'
            size = human_readable_size(item['size']) if human_readable else item['size']
            permissions = item['permissions']
            print(f"{file_type}{permissions} {size:>6} {time_formatted} {item['name']}")
        else:
            print(item['name'], end=' ')
    if not long_format:
        print()

def navigate_path(data, path):
    """Navigate through the JSON structure to find the path."""
    path_parts = path.strip('./').split('/')
    current = data['contents'] if 'contents' in data else data
    if not path_parts[0]:  # Current directory
        return current
    for part in path_parts:
        found = False
        for item in current:
            if isinstance(item, dict) and item.get('name') == part:
                if 'contents' in item:
                    current = item['contents']
                    found = True
                else:
                    return [item]
                break
        if not found:
            raise KeyError("No such file or directory")
    return current

def main():
    with open('structure.json') as f:
        data = json.load(f)
    parser = argparse.ArgumentParser(
        description='A simple implementation of ls command in Python',
        usage='python -m pyls.pyls [options] [path]',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-A', action='store_true', help='do not ignore entries starting with .')
    parser.add_argument('-l', action='store_true', help='use a long listing format')
    parser.add_argument('-r', action='store_true', help='reverse order while sorting')
    parser.add_argument('-t', action='store_true', help='sort by modification time, newest first')
    parser.add_argument('-H', action='store_true', help='human-readable sizes')
    parser.add_argument('--filter', type=str, choices=['file', 'dir'], help='filter by type (file or dir)')
    parser.add_argument('path', nargs='?', default='.', help='path to list (default: current directory)')
    args = parser.parse_args()
    try:
        contents = navigate_path(data, args.path)
        if len(contents) == 1 and 'contents' not in contents[0]:
            # Path is a file
            item = contents[0]
            if args.l:
                size = human_readable_size(item['size']) if args.H else item['size']
                time_formatted = datetime.fromtimestamp(item['time_modified']).strftime('%b %d %H:%M')
                file_type = '-' if 'contents' not in item else 'd'
                print(f"{file_type}{item['permissions']} {size:>6} {time_formatted} {args.path}")
            else:
                print(args.path)
        else:
            # Path is a directory
            print_ls(contents, show_all=args.A, long_format=args.l, reverse=args.r, sort_by_time=args.t, filter_type=args.filter, human_readable=args.H)
    except KeyError:
        print(f"error: cannot access '{args.path}': No such file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()

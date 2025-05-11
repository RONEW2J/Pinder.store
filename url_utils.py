from django.urls import get_resolver, URLPattern, URLResolver
import importlib

def print_urls_recursive(patterns, prefix=''):
    if not patterns:
        print(f"{prefix}  [No patterns found in this resolver/list]")
        return
    for pattern in patterns:
        # Try to get the regex pattern string; might need adjustment based on Django version/pattern type
        try:
            pattern_str = pattern.pattern.regex.pattern.lstrip('^').rstrip('$')
        except AttributeError:
            try:
                pattern_str = str(pattern.pattern) # Fallback for simpler patterns
            except AttributeError:
                pattern_str = "[Pattern N/A]"

        current_prefix = f"{prefix}{pattern_str}"

        if isinstance(pattern, URLResolver):
            namespace = getattr(pattern, 'namespace', '[No Namespace]')

            module_name_str = ''
            urlconf_name = getattr(pattern, 'urlconf_name', None)
            if isinstance(urlconf_name, str):
                module_name_str = f" (module string: {urlconf_name})"
            elif hasattr(urlconf_name, '__name__'):
                module_name_str = f" (module: {urlconf_name.__name__})"
            elif isinstance(urlconf_name, (list, tuple)):
                module_name_str = " (inline list of patterns)"

            print(f"Included Namespace: {namespace}{module_name_str} at prefix: {current_prefix}")

            if hasattr(pattern, 'url_patterns'):
                print_urls_recursive(pattern.url_patterns, prefix=current_prefix)

        elif isinstance(pattern, URLPattern):
            view_callback = getattr(pattern, 'callback', None)
            view_name_str = view_callback.__name__ if hasattr(view_callback, '__name__') else str(view_callback)
            url_name_str = getattr(pattern, 'name', '[No Name]')
            print(f"  Name: {url_name_str}, Pattern: {current_prefix}, View: {view_name_str}")
        else:
            print(f"  Unknown pattern type: {type(pattern)} with pattern: {current_prefix}")

def show_all_urls():
    root_resolver = get_resolver(None)
    print("Root URL Patterns:")
    if hasattr(root_resolver, 'url_patterns'):
        print_urls_recursive(root_resolver.url_patterns)
    else:
        print("Root resolver has no url_patterns attribute.")

def test_reverse(name, args_list=None):
    from django.urls import reverse, NoReverseMatch
    print(f"\nTrying to reverse '{name}' with args {args_list or []}:")
    try:
        url = reverse(name, args=args_list or [])
        print(f"SUCCESS: Reversed URL: {url}")
    except NoReverseMatch as e:
        print(f"ERROR (NoReverseMatch): {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")


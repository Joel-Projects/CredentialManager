from collections import OrderedDict

from apispec.ext.marshmallow.swagger import schema2parameters
from flask_restplus.swagger import Swagger as OriginalSwagger
from flask_restplus.swagger import extract_path_params, parse_docstring
from flask_restplus.utils import merge
from six import iteritems, string_types


class Swagger(OriginalSwagger):
    def parameters_for(self, doc):
        schema = doc["params"]

        if not schema:
            return []
        if isinstance(schema, list):  # pragma: no cover
            return schema
        if isinstance(schema, dict) and all(isinstance(field, dict) for field in schema.values()):
            return list(schema.values())

        if "in" in schema.context and "json" in schema.context["in"]:
            default_location = "body"
        else:
            default_location = "query"
        return schema2parameters(schema, default_in=default_location, required=True)

    def extract_resource_doc(self, resource, url):
        doc = getattr(resource, "__apidoc__", {})
        if doc is False:  # pragma: no cover
            return False
        doc["name"] = resource.__name__
        params = merge(self.expected_params(doc), doc.get("params", OrderedDict()))
        params = merge(params, extract_path_params(url))
        # Track parameters for late deduplication
        up_params = {(n, p.get("in", "query")): p for n, p in params.items()}
        need_to_go_down = set()
        methods = [m.lower() for m in resource.methods or []]
        for method in methods:
            method_doc = doc.get(method, OrderedDict())
            method_impl = getattr(resource, method)
            if hasattr(method_impl, "im_func"):  # pragma: no cover
                method_impl = method_impl.im_func
            elif hasattr(method_impl, "__func__"):  # pragma: no cover
                method_impl = method_impl.__func__
            method_doc = merge(method_doc, getattr(method_impl, "__apidoc__", OrderedDict()))
            if method_doc is not False:
                method_doc["docstring"] = parse_docstring(method_impl)
                method_params = self.expected_params(method_doc)
                method_params = merge(method_params, method_doc.get("params", {}))
                inherited_params = OrderedDict((k, v) for k, v in iteritems(params) if k in method_params)
                method_doc["params"] = merge(inherited_params, method_params)
                try:
                    for name, param in method_doc["params"].items():  # pragma: no cover
                        key = (name, param.get("in", "query"))
                        if key in up_params:
                            need_to_go_down.add(key)
                except AttributeError:
                    for name, param in method_doc["params"].__dict__.items():
                        if name == "session":
                            continue
                        if hasattr(param, "get"):
                            key = (name, param.get("in", "query"))
                            if key in up_params:  # pragma: no cover
                                need_to_go_down.add(key)

            doc[method] = method_doc
        # Deduplicate parameters
        # For each couple (name, in), if a method overrides it,
        # we need to move the paramter down to each method
        if need_to_go_down:  # pragma: no cover
            for method in methods:
                method_doc = doc.get(method)
                if not method_doc:
                    continue
                params = {(n, p.get("in", "query")): p for n, p in (method_doc["params"] or {}).items()}
                for key in need_to_go_down:
                    if key not in params:
                        method_doc["params"][key[0]] = up_params[key]
        doc["params"] = OrderedDict((k[0], p) for k, p in up_params.items() if k not in need_to_go_down)
        return doc

    def extract_tags(self, api):
        tags = []
        by_name = {}
        for tag in api.tags:  # pragma: no cover
            if isinstance(tag, string_types):
                tag = {"name": tag}
            elif isinstance(tag, (list, tuple)):
                tag = {"name": tag[0], "description": tag[1]}
            elif isinstance(tag, dict) and "name" in tag:
                pass
            else:
                raise ValueError(f"Unsupported tag format for {tag}")
            tags.append(tag)
            by_name[tag["name"]] = tag
        for ns in api.namespaces:
            if not ns.resources:
                continue
            if ns.name not in by_name:
                tags.append({"name": ns.name, "description": ns.description})
            elif ns.description:  # pragma: no cover
                by_name[ns.name]["description"] = ns.description
        return tags

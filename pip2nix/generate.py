from __future__ import unicode_literals

import logging
import os
import sys
from collections import OrderedDict
from tempfile import mkdtemp

from pip._internal.commands.freeze import FreezeCommand
from pip._internal.network.session import PipSession
from pip._internal.req.req_tracker import RequirementTracker
from pip._internal.operations.prepare import RequirementPreparer
from pip._internal.cache import WheelCache
from pip._internal import cmdoptions
from pip._internal.index.collector import LinkCollector
from pip._internal.models.search_scope import SearchScope
from pip._internal.models.index import PyPI

from .nix import NixPrefetchURL, nix_prefetch_url
from .utils import get_vcs_url
from .wheel import Wheel


class NixFreezeCommand(FreezeCommand):

    def run(self, options, args):
        self.temp_path = options.temp_path or mkdtemp(
            prefix='pip2nix-req-source-'
        )
        self.session = PipSession()
        options.cache_dir = os.path.expanduser(options.cache_dir)
        self.preparer = RequirementPreparer(
            build_dir=self.temp_path,
            src_dir=self.temp_path,
            download_dir=self.temp_path,
            build_isolation=options.build_isolation,
            req_tracker=RequirementTracker(),
            session=self.session,
            progress_bar=options.progress_bar,
            finder=self._build_package_finder(options),
            require_hashes=options.require_hashes,
            use_user_site=options.use_user_site,
            lazy_wheel=options.lazy_wheel,
            in_tree_build=options.in_tree_build,
        )

        return super(NixFreezeCommand, self).run(options, args)

    def _get_dist(self, req):
        if not req.source_dir:
            req.source_dir = self.preparer.prepare_linked_requirement(
                req
            ).source_dir

        if not req.source_dir:
            raise Exception(
                "Could not find source for %s" % req.name
            )

        dist = req.get_dist()
        if isinstance(dist, NixPrefetchURL):
            return dist

        # It's a source distribution. Let's now check if we have a VCS url
        vcs_url = get_vcs_url(req)
        if vcs_url:
            dist.vcs_url = vcs_url

        return dist

    def _build_package_finder(self, options):
        """Modified from pip's InstallCommand"""
        link_collector = LinkCollector(
            session=self.session,
            search_scope=SearchScope(
                find_links=options.find_links,
                index_urls=[options.index_url] + options.extra_index_urls,
                trusted_hosts=options.trusted_hosts,
            ),
        )
        wheel_cache = WheelCache(options.cache_dir, options.format_control)

        return super(NixFreezeCommand, self)._build_package_finder(
            options=options,
            session=self.session,
            link_collector=link_collector,
            wheel_cache=wheel_cache,
        )

"""Minimal base class for all protorpc API applications.

Functionality that is common to all APIs should go here.
""" 

from protorpc import remote
import common

class BaseApi(remote.Service):
  """Base class for protorpc service WSGI applications implementing APIs."""

  # Stash the request state so we can get at the HTTP headers later.
  # https://github.com/google/protorpc/blob/981174b77c87c222ac38fdc156bd7b2607b31531/protorpc/remote.py#L46
  def initialize_request_state(self, request_state):
    """request_state: a remote.RequestState instance"""
    self.rs = request_state

  def _authorize_staff(self):
    """Simply call this to ensure that the user has a Staff record.

    Raises:
      remote.ApplicationError if the user is not Staff.
    """
    user = common.RoomsUser.from_request(self.rs)
    if user and user.staff:
      return
    raise remote.ApplicationError('Must be staff to use this API.')

  def _authorize_user(self):
    """Simply call this to ensure that the user has a ROOMS record.

    Raises:
      remote.ApplicationError if the user is not Staff or Captain.
    """
    user = common.RoomsUser.from_request(self.rs)
    if user and (user.staff or user.captain):
      return
    raise remote.ApplicationError('Must be a ROOMS user to use this API.')

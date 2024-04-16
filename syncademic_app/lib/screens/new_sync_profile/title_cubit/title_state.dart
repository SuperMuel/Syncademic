part of 'title_cubit.dart';

@freezed
class TitleState with _$TitleState {
  const factory TitleState({@Default("") String title, String? error}) =
      _TitleState;

  const TitleState._();

  bool get isValid => error == null;
}
